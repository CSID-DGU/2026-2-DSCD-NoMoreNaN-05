from dataclasses import dataclass

CLAIM_TYPES = ("인물 자격", "제품 관계", "효능", "수치", "인증")


@dataclass
class VisualClaim:
    claim_id: str              # "v01", "v02", ...
    text: str                  # 화면 글자면 원문 그대로, 아니면 보이는 것의 짧은 서술
    t_start: float             # 노출 구간 (글자면 글자 구간, 아니면 샷 구간)
    t_end: float
    duration: float
    target: str | None         # 제품명 · 원료명 · 브랜드명, 불명확하면 None
    scope: str                 # IN_SCOPE | OUT_OF_SCOPE
    speaker: None              # 화면 Claim은 화자 없음
    dup_of: str | None
    types: list[str]
    source: str                # "화면"
    timestamp: float           # 근거 프레임 시각
    frame_index: int
    frame_path: str
