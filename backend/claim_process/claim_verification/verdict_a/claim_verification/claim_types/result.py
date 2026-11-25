"""A 판정 결과 한 건. 클레임 안의 대조 대상(원료 하나, 수치 하나) 하나의 결과다.

code는 사유 코드, reason은 사람이 읽는 설명이다. 왜 UNCLEAR인지는 이 둘로 남긴다.
evidence에는 비교에 실제로 쓴 근거만 {"field", "value"}로 담는다.
"""

from dataclasses import asdict, dataclass, field

from ..finding import SUPPORTED, UNCLEAR, VIOLATION

OUT_OF_SCOPE = "OUT_OF_SCOPE"
LABEL_ORDER = (VIOLATION, UNCLEAR, SUPPORTED, OUT_OF_SCOPE)


@dataclass
class Check:
    status: str
    code: str
    reason: str
    target: str | None = None
    claim_value: str | None = None
    evidence: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if self.status not in LABEL_ORDER:
            raise ValueError(f"알 수 없는 status: {self.status!r}")
        if not self.code or not self.reason:
            raise ValueError("code와 reason은 비울 수 없음")

    def to_dict(self) -> dict:
        return asdict(self)
