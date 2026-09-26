from dataclasses import dataclass

CLAIM_TYPES = ("인물 자격", "제품 관계", "효능", "수치", "인증")


@dataclass
class Claim:
    claim: str
    types: list[str]
    source: str
    start: float
    end: float
    duration: float
    segment_ids: list[int]
    quote: str = ""
