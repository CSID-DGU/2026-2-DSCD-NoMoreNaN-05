"""영상 한 편의 클레임을 claim_type별로 판정한다.

confirmed 제품의 클레임만 판정하고, 나머지는 사유와 함께 skipped로 내보낸다.
면책 문구는 타입과 상관없이 먼저 거른다. 클레임 담당이 면책 문구를 EFFECT로 분류하는 경우가 많아서다.
그 외 EFFECT는 메커니즘 B가 판정하므로 A 결과에 넣지 않는다.

판정 함수 모양: check(claim, product) -> list[Check]
"""

from typing import Callable

from ..disclaimer import DISCLAIMER, is_disclaimer
from ..finding import UNCLEAR
from ..inputs import CONFIRMED, NOT_FOUND
from .checkers.certification import check_certification
from .checkers.composition import make_check_composition
from .checkers.quantity import check_quantity
from .parsing.lexicon import Lexicon
from .result import LABEL_ORDER, OUT_OF_SCOPE, Check

Checker = Callable[[dict, dict], list[Check]]

EFFECT = "EFFECT"

# skipped 사유
PRODUCT_NOT_FOUND = "PRODUCT_NOT_FOUND"
PRODUCT_UNRESOLVED = "PRODUCT_UNRESOLVED"
NO_PRODUCT_REF = "NO_PRODUCT_REF"

NO_CHECKER = "NO_CHECKER"
NOT_VERIFIABLE_TYPE = "NOT_VERIFIABLE_TYPE"


def _not_verifiable(claim: dict, product: dict) -> list[Check]:
    return [Check(OUT_OF_SCOPE, NOT_VERIFIABLE_TYPE, f"{claim['claim_type']}은 근거 데이터로 검증하지 않음")]


# 타입을 구현할 때 하나씩 추가한다.
CHECKERS: dict[str, Checker] = {
    "PERSON_CREDENTIAL": _not_verifiable,
    "ETC": _not_verifiable,
    "QUANTITY": check_quantity,
    "COMPOSITION": make_check_composition(Lexicon.load()),
    "CERTIFICATION": check_certification,
}


def label(checks: list[Check]) -> str:
    statuses = {c.status for c in checks}
    for status in LABEL_ORDER:
        if status in statuses:
            return status
    return OUT_OF_SCOPE


def judge_claim(claim: dict, product: dict, checkers: dict[str, Checker]) -> dict:
    out = {k: claim.get(k) for k in ("claim_id", "product_ref", "text", "claim_type")}
    if is_disclaimer(claim["text"]):
        out.update(label=DISCLAIMER, reason_codes=[], checks=[])
        return out
    checker = checkers.get(claim.get("claim_type"))
    if checker is None:
        checks = [Check(UNCLEAR, NO_CHECKER, f"claim_type {claim.get('claim_type')!r}의 판정 함수가 없음")]
    else:
        checks = checker(claim, product)
    out["label"] = label(checks)
    out["reason_codes"] = list(dict.fromkeys(c.code for c in checks if c.status == out["label"]))
    out["checks"] = [c.to_dict() for c in checks]
    return out


def judge_video(video: dict, checkers: dict[str, Checker] | None = None) -> dict:
    checkers = CHECKERS if checkers is None else checkers
    products = {p["product_ref"]: p for p in video["products"]}
    claims, skipped = [], []
    for claim in video["claims"]:
        product = products.get(claim.get("product_ref"))
        if product is None:
            skipped.append({"claim_id": claim["claim_id"], "reason": NO_PRODUCT_REF})
        elif product["match"]["status"] != CONFIRMED:
            reason = PRODUCT_NOT_FOUND if product["match"]["status"] == NOT_FOUND else PRODUCT_UNRESOLVED
            skipped.append({"claim_id": claim["claim_id"], "reason": reason})
        elif claim.get("claim_type") != EFFECT or is_disclaimer(claim["text"]):
            claims.append(judge_claim(claim, product, checkers))
    return {
        "video_id": video["video_id"],
        "db_version": video.get("db_version"),
        "products": [{"product_ref": p["product_ref"],
                      "product_name": p.get("product_name"),
                      "manufacturing_report_number": p.get("manufacturing_report_number"),
                      "match_status": p["match"]["status"]} for p in video["products"]],
        "claims": claims,
        "skipped": skipped,
    }
