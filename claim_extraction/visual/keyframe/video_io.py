from pathlib import Path

import cv2
import numpy as np
from PIL import Image

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}


def list_inputs(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.iterdir() if p.suffix.lower() in VIDEO_EXTS)


class VideoReader:
    def __init__(self, path: Path):
        self.path = path
        self.cap = cv2.VideoCapture(str(path))
        if not self.cap.isOpened():
            raise RuntimeError(f"영상을 열 수 없음: {path}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.n_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.n_frames / self.fps

    def time_to_index(self, t: float) -> int:
        return min(max(int(round(t * self.fps)), 0), self.n_frames - 1)

    def index_to_time(self, i: int) -> float:
        return round(i / self.fps, 3)

    def frame(self, i: int) -> Image.Image:
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, bgr = self.cap.read()
        if not ok:
            raise RuntimeError(f"프레임 읽기 실패: {self.path.name} #{i}")
        return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

    def frames(self, start: int, count: int) -> np.ndarray:
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        out = []
        for _ in range(count):
            ok, bgr = self.cap.read()
            if not ok:
                break
            out.append(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        while len(out) < count:          # 영상 끝이면 마지막 프레임으로 채움
            out.append(out[-1])
        return np.stack(out)

    def save(self, i: int, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.frame(i).save(path, quality=90)

    def close(self):
        self.cap.release()
