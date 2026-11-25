import torch
from transformers import AutoModel, AutoVideoProcessor

from .schemas import Frame
from .video_io import VideoReader


def candidates(reader: VideoReader, interval: float) -> list[int]:
    """interval/2, 3·interval/2, … 초의 프레임 번호."""
    out = []
    k = 0
    while (k + 0.5) * interval < reader.duration:
        out.append(reader.time_to_index((k + 0.5) * interval))
        k += 1
    return sorted(set(out))


class ChangeDetector:

    def __init__(self, model: str, device: str = "cuda:0", n_frames: int = 64):
        self.device = device
        self.processor = AutoVideoProcessor.from_pretrained(model)
        self.model = AutoModel.from_pretrained(model, dtype=torch.bfloat16).to(device).eval()
        self.clip_len = self.model.config.frames_per_clip
        self.n_frames = n_frames                                   # clip_len 창에서 솎아 넣을 프레임 수

    @torch.no_grad()
    def embed(self, reader: VideoReader, center: int) -> torch.Tensor:
        start = max(0, min(center - self.clip_len // 2, reader.n_frames - self.clip_len))
        clip = reader.frames(start, self.n_frames, self.clip_len // self.n_frames)   # T x H x W x C
        inputs = self.processor(list(clip), return_tensors="pt").to(self.device)
        feats = self.model.get_vision_features(**inputs)           # 1 x N x D
        return torch.nn.functional.normalize(feats.mean(dim=1)[0].float(), dim=0)

    def select(
        self, reader: VideoReader, candidates: list[int], threshold: float, max_frames: int
    ) -> list[Frame]:
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
        top = sorted(kept, key=lambda k: k[1], reverse=True)[:max_frames]     # 상한을 넘으면 거리 작은 것부터 탈락
        return [Frame(idx, reader.index_to_time(idx), dist) for idx, dist in sorted(top)]
