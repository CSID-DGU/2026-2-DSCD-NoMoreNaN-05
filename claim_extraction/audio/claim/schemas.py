from dataclasses import dataclass

CLAIM_TYPES = ("인물 자격", "제품 관계", "효능", "수치", "인증")


@dataclass
class Claim:
    claim_id: str              # "a01", "a02", ...
    text: str                  # 대본에 실제 등장한 원문 그대로
    t_start: float
    t_end: float
    duration: float
    target: str | None         # 제품명 · 원료명 · 브랜드명, 불명확하면 None
    scope: str                 # IN_SCOPE | OUT_OF_SCOPE
    speaker: str | None        # narrator | quoted_person | None
    dup_of: str | None         # 반복 Claim이면 최초 Claim의 claim_id
    types: list[str]
    source: str                # "음성"
    segment_ids: list[int]
