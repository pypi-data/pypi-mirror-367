import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights


class MobileNetV3Backbone(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()

        # 加载 mobilenet_v3_small 预训练权重
        self.backbone = mobilenet_v3_small(
            weights=MobileNet_V3_Small_Weights.DEFAULT)
        
        # 获取原分类器输入特征数
        in_features = self.backbone.classifier[0].in_features

        # 替换分类头，定义新的分类层
        self.backbone.classifier = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


def mobilenet_v3(num_classes=3):

    # 自动选择设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 初始化网络
    model = MobileNetV3Backbone(num_classes)

    # 移动到对应的设备
    return model.to(device)

