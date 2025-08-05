import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from jxb_mobilenetv3.config import get_cfg
from jxb_mobilenetv3.src.mobilenet_v3 import mobilenet_v3
from jxb_mobilenetv3.src.dataset import get_data_loader
from jxb_mobilenetv3.utils import (
    save_checkpoint,
    save_training_log,
    plot_confusion_matrix,
    plot_training_metrics
)


def MobileNetV3Train(**args):

    # 初始化配置信息
    config = get_cfg(**args)
    print(f"Train Config\n{vars(config)}\n")

    # 创建训练输出文件夹
    os.makedirs(config.checkpoint_dir, exist_ok=True)

    # 设备设置
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device {device}')

    # 获取训练数据装载器以及类别名称
    train_loader, val_loader, class_names = get_data_loader(
        config.data_root, config.batch_size)

    # 获取类别数量
    num_classes = len(class_names)

    # 初始化模型
    model = mobilenet_v3(num_classes)

    # 冻结预训练的backbone参数
    for param in model.backbone.features.parameters():
        param.requires_grad = False

    # 定义损失函数
    criterion = nn.CrossEntropyLoss()

    # 定义优化器(梯度下降的方式)
    optimizer = optim.Adam(filter(lambda p: p.requires_grad,
                           model.parameters()), lr=config.lr, weight_decay=1e-4)

    # 学习率调度器
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.1, patience=3, verbose=True
    )

    # 加载检查点
    start_epoch = 0
    best_val_acc = 0.0

    # 训练循环
    for epoch in range(start_epoch, config.epochs):
        print(f"\nEpoch {epoch+1}/{config.epochs}")

        # 设置模型为训练模式
        model.train()
        running_loss = 0.0  # 所有数据在一个epoch的总损失
        correct = 0  # 所有数据在一个epoch的累计正确个数
        total = 0  # 总训练数据量

        # 进度条装载器
        pbar = tqdm(train_loader, desc='Train')
        for images, labels in pbar:

            # 将图片和标签移动到计算设备
            images, labels = images.to(device), labels.to(device)

            # 前向传播
            outputs = model(images)  # [batch_size, num_classes]

            # 计算模型损失(默认平均损失)
            loss = criterion(outputs, labels)

            # 清空梯度
            optimizer.zero_grad()

            # 反向传播
            loss.backward()

            # 更新参数
            optimizer.step()

            # 所有批次的总损失之和
            batch_size = images.size(0)
            running_loss += loss.item() * batch_size  # 由于损失函数输出为平均损失, 此处需要恢复为总损失

            # 获取logits分数最大的类别ID
            _, max_logits_id = outputs.max(1)  # predicted的形状为[num_classes]

            # 获取总样本数量
            total += batch_size

            # 比较正确的预测结果数量
            batch_correct = max_logits_id.eq(labels).sum().item()
            correct += batch_correct

            # 更新进度条
            pbar.set_postfix({
                # 当前epoch的loss
                'batch_loss': f"{loss.item():.4f}",

                # 当前epoch的精度
                'batch_acc': f"{(batch_correct / batch_size):.4f}"
            })

        # 整个训练集的平均损失
        train_loss = running_loss / len(train_loader.dataset)

        # 整个训练集的平均精度
        train_acc = correct / total

        # 模型验证
        val_loss, val_acc = val(model, val_loader, criterion, device)

        # 学习率调整
        scheduler.step(val_loss)

        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")

        # 保存训练日志到CSV
        save_training_log(
            log_dir=config.checkpoint_dir,
            epoch=epoch + 1,
            train_loss=train_loss,
            train_acc=train_acc,
            val_loss=val_loss,
            val_acc=val_acc
        )

        is_best = val_acc > best_val_acc
        best_val_acc = max(val_acc, best_val_acc)

        save_checkpoint({
            'epoch': epoch,
            'state_dict': model.state_dict(),
            'best_val_acc': best_val_acc,
            'optimizer': optimizer.state_dict(),
            'class_names': class_names
        }, is_best, config.checkpoint_dir)

    # 训练结束后绘制指标图表
    print("\n训练完成, 正在生成可视化图表...")

    # 1. 绘制训练曲线
    plot_training_metrics(log_dir=config.checkpoint_dir)

    # 2. 绘制混淆矩阵
    plot_confusion_matrix(
        model=model,
        data_loader=val_loader,
        class_names=class_names,
        device=device,
        output_dir=config.checkpoint_dir
    )

    print("所有训练结果和图表已保存至:", config.checkpoint_dir)


def val(model, val_loader, criterion, device):

    # 开启评估模式（关闭Dropout/BatchNorm等）
    model.eval()
    running_loss = 0.0  # 所有数据在一个epoch的总损失
    correct = 0  # 所有数据在一个epoch的累计正确个数
    total = 0  # 总训练数据量

    # 关闭梯度计算
    with torch.no_grad():
        pbar = tqdm(val_loader, desc="Val")
        for images, labels in pbar:

            # 将数据转移到目标设备
            images, labels = images.to(device), labels.to(device)

            # 当前批次样本数
            batch_size = images.size(0)

            # 前向传播：模型推理 + 计算损失
            outputs = model(images)       # 模型输出（logits）

            # 计算损失
            loss = criterion(outputs, labels)

            # 统计基础指标
            running_loss += loss.item() * batch_size  # 累计损失（带批次权重）
            _, predicted = outputs.max(1)             # 预测标签（取概率最大的类别）
            correct += predicted.eq(labels).sum().item()  # 累计正确数
            total += batch_size  # 累计总样本数

            # 更新进度条显示（实时展示当前批次和平均指标）
            pbar.set_postfix({
                "batch_loss": f"{loss.item():.4f}",  # 当前批次损失
                "batch_acc": f"{correct / total:.4f}"  # 平均准确率（百分比格式）
            })

    # 计算最终基础指标（平均损失和整体准确率）
    val_loss = running_loss / total
    val_acc = correct / total

    return val_loss, val_acc
