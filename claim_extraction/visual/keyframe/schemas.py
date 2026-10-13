from dataclasses import dataclass


@dataclass
class Shot:
    id: int
    start: float
    end: float


@dataclass
class TextSpan:
    text: str
    start: float
    end: float
    frame_index: int


@dataclass
class Keyframe:
    frame_index: int
    timestamp: float
    source: str            # "change" / "text"
    shot_id: int
    shot_start: float
    shot_end: float
    text: str = ""         # 이 프레임의 OCR 결과
    text_start: float | None = None   # source == "text"일 때 글자 노출 구간
    text_end: float | None = None
    path: str = ""         # 저장된 이미지 경로
