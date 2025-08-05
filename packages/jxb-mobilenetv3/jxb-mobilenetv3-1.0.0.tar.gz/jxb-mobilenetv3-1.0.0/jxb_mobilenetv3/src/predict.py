import cv2
import torch
import numpy as np
from collections import Counter
from types import SimpleNamespace
from jxb_mobilenetv3.config import get_cfg
from jxb_mobilenetv3.src.mobilenet_v3 import mobilenet_v3


class MobileNetV3Predictor:
    def __init__(self, model_path, verbose=True):
        # 详细显示
        self.verbose = verbose

        # 自动选择设备
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 获取模型信息和加载好的模型
        self.checkpoint, self.model = self._load_model(model_path)

        # 获取类别名称映射字典
        self.class_names = self.checkpoint.class_names

        # 参数获取
        cfg = get_cfg()

        # 获取模型输入尺寸
        self.img_size = cfg.img_size

        # ImageNet 数据
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]

    def _load_model(self, model_path):
        # 加载模型信息
        checkpoint = SimpleNamespace(**torch.load(model_path, map_location=self.device))

        # 激活网络
        model = mobilenet_v3(len(checkpoint.class_names))

        # 加载训练好的权重
        model.load_state_dict(checkpoint.state_dict)

        # 将模型移动到指定设备
        model.to(self.device)

        # 开始推理模式
        model.eval()

        return checkpoint, model

    def _preprocess_cv2_batch(self, img_list):

        # resize 图片缓存
        resized_imgs = []
        for img in img_list:
            resized = cv2.resize(img, (self.img_size, self.img_size)).astype(np.float32)
            resized_imgs.append(resized)

        # 堆叠 RGB 图片
        imgs_rgb = np.stack([cv2.cvtColor(img, cv2.COLOR_BGR2RGB) for img in resized_imgs])
        imgs_rgb /= 255.0  # 归一化到0~1

        imgs_rgb = np.transpose(imgs_rgb, (0, 3, 1, 2))  # NHWC->NCHW

        mean = np.array(self.mean).reshape(1, 3, 1, 1)
        std = np.array(self.std).reshape(1, 3, 1, 1)
        imgs_rgb = (imgs_rgb - mean) / std

        # numpy 转换 tensor
        batch_tensor = torch.from_numpy(imgs_rgb)
        batch_tensor = batch_tensor.float().to(self.device)

        return batch_tensor

    def predict(self, img_list):
        if not isinstance(img_list, list):
            raise ValueError("img_list should be list of numpy arrays")

        # 堆叠批次
        batch_tensor = self._preprocess_cv2_batch(img_list)

        with torch.no_grad():
            outputs = self.model(batch_tensor)
            preds = torch.argmax(outputs, dim=1)
            exp_logits = torch.exp(outputs)
            sum_exp = torch.sum(exp_logits, dim=1)
            confs = (exp_logits[torch.arange(outputs.size(0)), preds] / sum_exp).cpu().numpy()
            class_ids = preds.cpu().numpy()

        # 清理显存
        del batch_tensor, outputs, preds, exp_logits, sum_exp
        torch.cuda.empty_cache()

        result_array = np.vstack((class_ids, confs))
        id_to_class = {i: name for i, name in enumerate(self.class_names)}

        return result_array, id_to_class

    def vote_predict(self, img_list):
        result_array, id_to_class = self.predict(img_list)
        class_ids = result_array[0]
        confidences = result_array[1]
        counts = Counter(class_ids)
        max_count = max(counts.values())
        candidates = [cls_id for cls_id, cnt in counts.items() if cnt == max_count]

        if len(candidates) == 1:
            voted_id = candidates[0]
        else:
            conf_sums = {cls_id: confidences[class_ids == cls_id].sum() for cls_id in candidates}
            voted_id = max(conf_sums, key=conf_sums.get)

        voted_label = id_to_class[voted_id]

        if self.verbose:
            print(f"投票结果 ➜ {voted_label}")

        return voted_label
