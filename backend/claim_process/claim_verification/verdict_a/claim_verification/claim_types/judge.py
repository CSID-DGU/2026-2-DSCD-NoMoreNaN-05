"""영상 한 편의 클레임을 claim_type별로 판정한다.

confirmed 제품의 클레임만 판정하고, 나머지는 사유와 함께 skipped로 내보낸다.
면책 문구는 타입과 상관없이 먼저 거른다. 클레임 담당이 면책 문구를 EFFECT로 분류하는 경우가 많아서다.
면책 문구와 ETC만 붙은 클레임은 제품 정보가 필요 없으므로 제품이 없거나 미확정이어도 판정한다.

한 클레임에 타입이 여러 개면 A 타입(QUANTITY·COMPOSITION·CERTIFICATION·PERSON_CREDENTIAL)마다 판정하고
결과를 모아 라벨 하나를 낸다(LABEL_ORDER에서 가장 앞선 것). ETC는 판정 대상 타입에서 뺀다.
EFFECT는 메커니즘 B가 판정한다. EFFECT가 붙은 클레임은 for_b에 넣고, A 타입이 함께 있으면 A 결과에도 남긴다.
EFFECT만 있는 클레임은 A 결과에 넣지 않는다. A·B를 합친 최종 라벨은 이 모듈에서 내지 않는다.

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
from .tags import CERTIFICATION, COMPOSITION, EFFECT, PERSON_CREDENTIAL, QUANTITY, claim_types, types_of

Checker = Callable[[dict, dict], list[Check]]

# skipped 사유
PRODUCT_NOT_FOUND = "PRODUCT_NOT_FOUND"
PRODUCT_UNRESOLVED = "PRODUCT_UNRESOLVED"
NO_PRODUCT_REF = "NO_PRODUCT_REF"

NO_CHECKER = "NO_CHECKER"
NO_CLAIM_TYPE = "NO_CLAIM_TYPE"
NOT_A_CLAIM = "NOT_A_CLAIM"
NOT_VERIFIABLE_TYPE = "NOT_VERIFIABLE_TYPE"


def _not_verifiable(claim: dict, product: dict) -> list[Check]:
    return [Check(OUT_OF_SCOPE, NOT_VERIFIABLE_TYPE, f"{PERSON_CREDENTIAL}은 근거 데이터로 검증하지 않음")]


# 타입을 구현할 때 하나씩 추가한다.
CHECKERS: dict[str, Checker] = {
    PERSON_CREDENTIAL: _not_verifiable,
    QUANTITY: check_quantity,
    COMPOSITION: make_check_composition(Lexicon.load()),
    CERTIFICATION: check_certification,
}


def label(checks: list[Check]) -> str:
    statuses = {c.status for c in checks}
    for status in LABEL_ORDER:
        if status in statuses:
            return status
    return OUT_OF_SCOPE


def _checks_by_type(claim: dict, product: dict, checkers: dict[str, Checker]) -> list[tuple[str | None, Check]]:
    if not types_of(claim):
        return [(None, Check(UNCLEAR, NO_CLAIM_TYPE, "claim_type이 비어 있음"))]
    a_types = [t for t in claim_types(claim) if t != EFFECT]
    if not claim_types(claim):
        return [(None, Check(OUT_OF_SCOPE, NOT_A_CLAIM, "ETC만 붙어 있어 주장으로 보지 않음"))]
    out = []
    for claim_type in a_types:
        checker = checkers.get(claim_type)
        if checker is None:
            out.append((claim_type, Check(UNCLEAR, NO_CHECKER, f"claim_type {claim_type!r}의 판정 함수가 없음")))
        else:
            out.extend((claim_type, c) for c in checker(claim, product))
    return out


def judge_claim(claim: dict, product: dict, checkers: dict[str, Checker]) -> dict:
    out = {k: claim.get(k) for k in ("claim_id", "product_ref", "text")}
    out["claim_type"] = types_of(claim)
    if is_disclaimer(claim["text"]):
        out.update(label=DISCLAIMER, reason_codes=[], checks=[])
        return out
    typed = _checks_by_type(claim, product, checkers)
    checks = [c for _, c in typed]
    out["label"] = label(checks)
    out["reason_codes"] = list(dict.fromkeys(c.code for c in checks if c.status == out["label"]))
    out["checks"] = [{"claim_type": t, **c.to_dict()} for t, c in typed]
    return out


def _for_b(claim: dict) -> bool:
    return EFFECT in claim_types(claim) and not is_disclaimer(claim["text"])


def _in_a(claim: dict) -> bool:
    """A 결과에 남길지. EFFECT만 있고 면책 문구가 아니면 B 몫이다."""
    return not _for_b(claim) or any(t != EFFECT for t in claim_types(claim))


def _needs_product(claim: dict) -> bool:
    """면책 문구와 판정 대상 타입이 없는 클레임(ETC만, 타입 없음)은 제품 정보 없이 라벨이 정해진다."""
    return bool(claim_types(claim)) and not is_disclaimer(claim["text"])


def judge_video(video: dict, checkers: dict[str, Checker] | None = None) -> dict:
    checkers = CHECKERS if checkers is None else checkers
    products = {p["product_ref"]: p for p in video["products"]}
    claims, skipped, for_b = [], [], []
    for claim in video["claims"]:
        if not _needs_product(claim):
            claims.append({**judge_claim(claim, None, checkers), "for_b": False})
            continue
        product = products.get(claim.get("product_ref"))
        if product is None:
            skipped.append({"claim_id": claim["claim_id"], "reason": NO_PRODUCT_REF})
            continue
        if product["match"]["status"] != CONFIRMED:
            reason = PRODUCT_NOT_FOUND if product["match"]["status"] == NOT_FOUND else PRODUCT_UNRESOLVED
            skipped.append({"claim_id": claim["claim_id"], "reason": reason})
            continue
        if _for_b(claim):
            for_b.append(claim["claim_id"])
        if _in_a(claim):
            claims.append({**judge_claim(claim, product, checkers), "for_b": _for_b(claim)})
    return {
        "video_id": video["video_id"],
        "db_version": video.get("db_version"),
        "products": [{"product_ref": p["product_ref"],
                      "product_name": p.get("product_name"),
                      "manufacturing_report_number": p.get("manufacturing_report_number"),
                      "match_status": p["match"]["status"]} for p in video["products"]],
        "claims": claims,
        "for_b": for_b,
        "skipped": skipped,
    }
