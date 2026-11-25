from dataclasses import dataclass


@dataclass
class Word:
    text: str
    start: float
    end: float


@dataclass
class Segment:
    id: int
    text: str
    start: float
    end: float
    char_start: int        # 본문(transcript) 안 위치 [char_start, char_end)
    char_end: int
