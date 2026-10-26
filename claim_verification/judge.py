"""클레임마다 조항 검사를 돌리고 라벨을 붙인다.

영상 하나에는 제품이 하나만 온다(DB 담당이 정제해서 넘김). product_ref가 null인 클레임도
그 제품에 대한 설명으로 보고 같은 제품으로 판정한다.

조항 함수 모양: check(claim, product) -> Finding | None
    자기 대상이 아니면 None을 돌려준다(기록 안 함). claim_type으로 거르지 않고 모든 클레임에 돌린다.
"""

from typing import Callable

from .finding import OVERCLAIM, SUPPORTED, UNCLEAR, VIOLATION, Finding

Check = Callable[[dict, dict], Finding | None]

CHECKS: list[Check] = []  # 조항을 구현할 때 하나씩 추가한다.

OUT_OF_SCOPE = "OUT_OF_SCOPE"
LABEL_ORDER = (VIOLATION, OVERCLAIM, UNCLEAR, SUPPORTED)

CHECKED = "CHECKED"
NO_CLAIMS = "NO_CLAIMS"

# 결과 클레임에 그대로 넘기는 handoff 필드. evidences 원본은 넣지 않는다.
PASS_THROUGH = ("claim_id", "product_ref", "text", "claim_type")


def label(findings: list[Finding]) -> str:
    statuses = {f.status for f in findings}
    for status in LABEL_ORDER:
        if status in statuses:
            return status
    return OUT_OF_SCOPE


def judge_claim(claim: dict, product: dict, checks: list[Check]) -> dict:
    findings = [f for check in checks if (f := check(claim, product)) is not None]
    out = {k: claim.get(k) for k in PASS_THROUGH}
    out["label"] = label(findings)
    out["findings"] = [f.to_dict() for f in findings]
    return out


def judge_video(video: dict, checks: list[Check] | None = None) -> dict:
    checks = CHECKS if checks is None else checks
    claims = video["claims"]
    product = video["products"][0]
    return {
        "video_id": video["video_id"],
        "status": CHECKED if claims else NO_CLAIMS,
        "product": product,
        "claims": [judge_claim(c, product, checks) for c in claims],
    }
