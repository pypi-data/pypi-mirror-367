import torch
import os
import csv
import shutil
import numpy as np
import seaborn as sns
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from jxb_mobilenetv3.config import TRAIN_TRANSFORMS, VAL_TRANSFORMS


def save_training_log(log_dir, epoch, train_loss, train_acc, val_loss, val_acc, is_new_training=False):

    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)

    # 确定日志文件路径
    log_path = os.path.join(log_dir, "training_log.csv")

    # 检查文件是否存在
    file_exists = os.path.exists(log_path)

    # 打开文件（追加模式）
    with open(log_path, 'a', newline='') as f:
        writer = csv.writer(f)

        # 如果是新文件或新训练，写入表头
        if not file_exists or is_new_training:
            writer.writerow(
                ['epoch', 'train_loss', 'train_acc', 'val_loss', 'val_acc'])

        # 写入当前轮次的数据
        writer.writerow([
            epoch,
            f"{train_loss:.6f}",
            f"{train_acc:.6f}",
            f"{val_loss:.6f}",
            f"{val_acc:.6f}"
        ])


def plot_training_metrics(log_dir, output_dir=None):

    # 设置输出目录
    if output_dir is None:
        output_dir = log_dir
    os.makedirs(output_dir, exist_ok=True)

    # 读取训练日志
    log_path = os.path.join(log_dir, "training_log.csv")

    # 读取CSV数据
    df = pd.read_csv(log_path)

    # 获取最大epoch值
    max_epoch = df['epoch'].max()

    # 1. 绘制损失曲线图
    plt.figure(figsize=(10, 6), dpi=300)
    plt.plot(df['epoch'], df['train_loss'], 'b-', label='Train Loss')
    plt.plot(df['epoch'], df['val_loss'], 'r-', label='Val Loss')

    # 设置横坐标刻度
    if max_epoch <= 10:
        plt.xticks(range(1, max_epoch+1))
    else:
        # 计算5的倍数刻度
        ticks = [i for i in range(0, max_epoch+1, 5) if i > 0]
        # 确保包含最后一个epoch
        if max_epoch not in ticks:
            ticks.append(max_epoch)
        plt.xticks(ticks)

    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.grid(False)

    # 保存损失曲线图
    loss_path = os.path.join(output_dir, "loss_curve.png")
    plt.tight_layout()
    plt.savefig(loss_path, dpi=300)
    plt.close()
    print(f"损失曲线已保存至: {loss_path}")

    # 2. 绘制精度曲线图
    plt.figure(figsize=(10, 6), dpi=300)
    plt.plot(df['epoch'], df['train_acc'], 'b-', label='Train Accuracy')
    plt.plot(df['epoch'], df['val_acc'], 'r-', label='Val Accuracy')

    # 设置横坐标刻度（与损失曲线相同）
    if max_epoch <= 10:
        plt.xticks(range(1, max_epoch+1))
    else:
        plt.xticks(ticks)

    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.legend()
    plt.grid(False)

    # 保存精度曲线图
    acc_path = os.path.join(output_dir, "accuracy_curve.png")
    plt.tight_layout()
    plt.savefig(acc_path, dpi=300)
    plt.close()
    print(f"精度曲线已保存至: {acc_path}")


def plot_confusion_matrix(model, data_loader, class_names, device, output_dir=None):

    if output_dir is None:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    # 设置模型为评估模式
    model.eval()

    # 收集所有预测和标签
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in tqdm(data_loader, desc="生成混淆矩阵"):
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # 计算混淆矩阵
    cm = confusion_matrix(all_labels, all_preds)
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]  # 归一化

    # 绘制混淆矩阵
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt=".2f", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Normalized Confusion Matrix')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)

    # 保存混淆矩阵
    cm_path = os.path.join(output_dir, "confusion_matrix.png")
    plt.tight_layout()
    plt.savefig(cm_path)
    plt.close()
    print(f"混淆矩阵已保存至: {cm_path}")


def train_val_transforms(type):
    return TRAIN_TRANSFORMS if type == 'train' else VAL_TRANSFORMS

def save_checkpoint(state, is_best, checkpoint_dir, filename='last.pt'):

    # 设置模型保存路径
    filepath = os.path.join(checkpoint_dir, filename)
    torch.save(state, filepath)

    # 检测是否为最优模型
    if is_best:

        # 将最优模型另存
        shutil.copyfile(filepath, os.path.join(
            checkpoint_dir, 'best.pt'))

