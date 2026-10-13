import torch
from transformers import AutoModel, AutoVideoProcessor

from .video_io import VideoReader


class ChangeDetector:

    def __init__(self, model: str, device: str = "cuda:0"):
        self.device = device
        self.processor = AutoVideoProcessor.from_pretrained(model)
        self.model = AutoModel.from_pretrained(model, dtype=torch.bfloat16).to(device).eval()
        self.clip_len = self.model.config.frames_per_clip

    @torch.no_grad()
    def embed(self, reader: VideoReader, center: int) -> torch.Tensor:
        start = max(0, min(center - self.clip_len // 2, reader.n_frames - self.clip_len))
        clip = reader.frames(start, self.clip_len)                 # T x H x W x C
        inputs = self.processor(list(clip), return_tensors="pt").to(self.device)
        feats = self.model.get_vision_features(**inputs)           # 1 x N x D
        return torch.nn.functional.normalize(feats.mean(dim=1)[0].float(), dim=0)

    def select(
        self, reader: VideoReader, candidates: list[int], threshold: float
    ) -> list[tuple[int, float]]:
        kept: list[tuple[int, float]] = []
        prev = None
        for idx in candidates:
            vec = self.embed(reader, idx)
            if prev is None:
                kept.append((idx, 1.0))
                prev = vec
                continue
            dist = float(1.0 - torch.dot(prev, vec))
            if dist >= threshold:
                kept.append((idx, dist))
                prev = vec
        return kept
