from dataclasses import dataclass, field



@dataclass
class AlignedClaim:
    claim_id: str              # "c01", "c02", ...
    text: str                  # 원문 그대로 (음성+화면이면 음성 원문)
    t_start: float             # 참조한 branch Claim들의 min/max
    t_end: float
    duration: float
    target: str | None         # 지시어 해소 결과는 text가 아니라 여기에 들어간다
    scope: str
    speaker: str | None        # 화면 전용이면 None
    dup_of: str | None
    types: list[str]           # 참조한 branch Claim들의 types 합집합
    source: str                # 음성 / 화면 / 음성+화면
    conflict: str | None       # 같은 시각에 내용이 어긋나는 Claim의 claim_id
    evidence: dict = field(default_factory=lambda: {"audio": [], "visual": []})
