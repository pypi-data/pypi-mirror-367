import torch
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from jxb_mobilenetv3.utils import train_val_transforms


class MobileNetV3Datasets(Dataset):
    def __init__(self, root, transforms=None, mode='train'):

        # 设置初始化参数
        self.root = Path(root)
        self.transforms = transforms

        # 获取类别
        self.class_names = sorted(
            [d.name for d in self.root.iterdir() if d.is_dir()])

        # 类别ID映射
        self.class_to_id = {cls: id for id, cls in enumerate(self.class_names)}

        # 设置样本集
        self.samples = []

        # 添加样本
        for cls in tqdm(self.class_names, desc=f'Loading {mode} data'):
            cls_dir = self.root / cls
            for img_path in cls_dir.iterdir():

                # 单个样本形状为 [图片路径, 类别映射ID]
                self.samples.append((str(img_path), self.class_to_id[cls]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        img_path, label = self.samples[index]
        with Image.open(img_path) as img:
            img = img.convert('RGB')
            if self.transforms:
                img = self.transforms(img)

        return img, torch.tensor(label, dtype=torch.long)

    def get_class_names(self):

        # 获取类别名称
        return self.class_names


def get_data_loader(root, batch_size=32):

    # 设置数据集根路径
    root = Path(root)

    # 分别获取训练和验证的数据路径
    train_dir = root / 'train'
    val_dir = root / 'val'

    # 构建训练和验证数据集
    train_dataset = MobileNetV3Datasets(
        train_dir, train_val_transforms('train'), mode='train')
    val_dataset = MobileNetV3Datasets(
        val_dir, train_val_transforms('val'), mode='val')

    # 构建训练和验证数据装载器
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=4, 
        pin_memory=True,
        prefetch_factor=2,
        persistent_workers=True
    )

    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size,
        shuffle=False, 
        num_workers=4, 
        pin_memory=True,
        prefetch_factor=2,
        persistent_workers=True
    )

    return train_loader, val_loader, train_dataset.get_class_names()

