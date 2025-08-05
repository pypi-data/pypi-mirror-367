from pathlib import Path
from types import SimpleNamespace
import yaml
from torchvision import transforms as T

__all__ = (
    "get_cfg",
    "TRAIN_TRANSFORMS",
    "VAL_TRANSFORMS"
)

# 动态设置项目文件路径
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
SRC = ROOT / "src"
CONFIG_PATH = ROOT / "config/config.yaml"


def get_cfg(**overrides):
    with open(CONFIG_PATH) as cfg:
        config = yaml.safe_load(cfg)

    if overrides:
        config = {**config, **overrides}

    return SimpleNamespace(**config)


IMG_SIZE = get_cfg().img_size


TRAIN_TRANSFORMS = T.Compose([
    T.Resize((IMG_SIZE, IMG_SIZE)),
    T.RandomHorizontalFlip(p=0.5),
    T.ColorJitter(0.2, 0.2, 0.2),
    T.RandomRotation(15),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

VAL_TRANSFORMS = T.Compose([
    T.Resize((IMG_SIZE, IMG_SIZE)),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
