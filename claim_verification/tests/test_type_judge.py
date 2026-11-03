import pytest

from claim_verification.claim_types.judge import judge_claim, judge_video, label
from claim_verification.claim_types.result import OUT_OF_SCOPE, Check
from claim_verification.finding import SUPPORTED, UNCLEAR, VIOLATION


def _claim(claim_id="c01", ref="p01", text="관절 건강", claim_type="EFFECT"):
    return {"claim_id": claim_id, "product_ref": ref, "text": text, "claim_type": claim_type}


def _video(claims, status="confirmed"):
    product = {"product_ref": "p01", "product_name": "제품", "manufacturing_report_number": "123",
               "match": {"status": status}, "DB": {}}
    return {"video_id": "v1", "products": [product], "claims": claims}


def _found(status, code="C", target="아연"):
    return lambda claim, product: [Check(status, code, "이유", target=target)]


def test_check_needs_code_and_reason():
    with pytest.raises(ValueError):
        Check(UNCLEAR, "C", "")
    with pytest.raises(ValueError):
        Check("OVERCLAIM", "C", "이유")


def test_label_takes_worst_status():
    checks = [Check(SUPPORTED, "A", "이유"), Check(UNCLEAR, "B", "이유"), Check(VIOLATION, "C", "이유")]
    assert label(checks) == VIOLATION
    assert label(checks[:2]) == UNCLEAR
    assert label([]) == OUT_OF_SCOPE


def test_partly_matched_claim_is_not_supported():
    checkers = {"COMPOSITION": lambda c, p: [Check(SUPPORTED, "FOUND", "있음", target="아연"),
                                             Check(UNCLEAR, "UNMATCHED", "사전에 없음", target="LACTO-5X")]}
    out = judge_claim(_claim(claim_type="COMPOSITION"), {}, checkers)
    assert out["label"] == UNCLEAR
    assert out["reason_codes"] == ["UNMATCHED"]
    assert [c["target"] for c in out["checks"]] == ["아연", "LACTO-5X"]


def test_disclaimer_comes_before_checker():
    text = "본 제품은 질병의 예방 및 치료를 위한 의약품이 아닙니다"
    out = judge_claim(_claim(text=text), {}, {"EFFECT": _found(VIOLATION)})
    assert out["label"] == "DISCLAIMER"
    assert out["checks"] == []


def test_effect_is_left_to_mechanism_b():
    assert judge_video(_video([_claim()]))["claims"] == []


def test_effect_disclaimer_stays_in_a():
    text = "본 제품은 질병의 예방 및 치료를 위한 의약품이 아닙니다"
    out = judge_video(_video([_claim(text=text)]))["claims"][0]
    assert out["label"] == "DISCLAIMER"
    assert "next" not in out


@pytest.mark.parametrize("claim_type", ["PERSON_CREDENTIAL", "ETC"])
def test_unverifiable_types_are_out_of_scope(claim_type):
    out = judge_video(_video([_claim(claim_type=claim_type)]))["claims"][0]
    assert out["label"] == OUT_OF_SCOPE
    assert out["reason_codes"] == ["NOT_VERIFIABLE_TYPE"]


def test_type_without_checker_is_unclear_with_reason():
    out = judge_claim(_claim(claim_type="NEW"), {}, {})
    assert out["label"] == UNCLEAR
    assert out["reason_codes"] == ["NO_CHECKER"]


@pytest.mark.parametrize("status,reason", [("not_found", "PRODUCT_NOT_FOUND"), ("unresolved", "PRODUCT_UNRESOLVED")])
def test_unconfirmed_product_is_skipped(status, reason):
    result = judge_video(_video([_claim()], status=status))
    assert result["claims"] == []
    assert result["skipped"] == [{"claim_id": "c01", "reason": reason}]


def test_claim_without_product_is_skipped():
    result = judge_video(_video([_claim(ref=None)]))
    assert result["skipped"] == [{"claim_id": "c01", "reason": "NO_PRODUCT_REF"}]


def test_output_keeps_only_product_summary():
    result = judge_video(_video([]))
    assert result["products"] == [{"product_ref": "p01", "product_name": "제품",
                                   "manufacturing_report_number": "123", "match_status": "confirmed"}]
