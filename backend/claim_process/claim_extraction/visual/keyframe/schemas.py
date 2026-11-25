from dataclasses import dataclass


@dataclass
class TextSpan:
    text: str
    start: float
    end: float
    t_rep: float           # 대표 변형(text)이 처음 읽힌 프레임 시각. 타이핑 중이면 start보다 늦다
    frame_index: int


@dataclass
class Frame:
    frame_index: int
    timestamp: float
    distance: float | None  # 직전에 남긴 프레임과의 V-JEPA 거리(1 − cos). 첫 프레임은 1.0, text 프레임은 None
    path: str = ""         # 저장된 이미지 경로
    source: str = "change"  # 고른 선택기: change(V-JEPA 2) / text(OCR 대표 표기 프레임)
