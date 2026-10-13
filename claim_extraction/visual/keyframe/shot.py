from pathlib import Path

import torch
from transnetv2_pytorch import TransNetV2

from .schemas import Shot


class ShotDetector:
    def __init__(self, device: str = "cuda:0", threshold: float = 0.5):
        self.model = TransNetV2(device=device)
        self.model.eval()
        self.threshold = threshold

    def detect(self, video: Path) -> list[Shot]:
        with torch.no_grad():
            scenes = self.model.detect_scenes(str(video), threshold=self.threshold)
        return [
            Shot(id=i, start=round(float(s["start_time"]), 3), end=round(float(s["end_time"]), 3))
            for i, s in enumerate(scenes)
        ]
