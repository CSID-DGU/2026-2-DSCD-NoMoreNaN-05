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
