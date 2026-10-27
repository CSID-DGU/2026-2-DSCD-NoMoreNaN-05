"""조항 결과(finding) 한 건. 클레임 하나 × 조항(목) 하나의 판정이다.

status는 아래 네 개 중 하나다. 사유 코드(code)는 조항을 구현할 때 그 조항 모듈에 둔다.
evidence에는 비교에 실제로 쓴 handoff evidence만 {"source_ref", "text"}로 담는다.
"""

from dataclasses import asdict, dataclass, field

VIOLATION = "VIOLATION"
OVERCLAIM = "OVERCLAIM"
UNCLEAR = "UNCLEAR"
SUPPORTED = "SUPPORTED"
STATUSES = (VIOLATION, OVERCLAIM, UNCLEAR, SUPPORTED)


@dataclass
class Finding:
    status: str
    code: str
    law_ref: str
    span: str
    detail: str
    evidence: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError(f"알 수 없는 status: {self.status!r}")

    def to_dict(self) -> dict:
        return asdict(self)

