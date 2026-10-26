from pathlib import Path

import pytest

from claim_verification.inputs import HandoffError, load_handoff, validate_video

# 형식 견본(DB 담당 handoff). 로컬에만 있다.
NEM = Path(__file__).resolve().parents[2] / "data/fixtures/nem_claim_evidence_handoff.json"


def video(**claim_overrides):
    claim = {"claim_id": "c01", "product_ref": "p01", "text": "건강기능식품", "evidences": []}
    claim.update(claim_overrides)
    return {"video_id": "v1", "products": [{"product_ref": "p01"}], "claims": [claim]}


def test_valid_video_passes():
    validate_video(video())


def test_missing_claim_field_names_location():
    data = video()
    del data["claims"][0]["evidences"]
    with pytest.raises(HandoffError, match="v1/c01"):
        validate_video(data)


@pytest.mark.parametrize("n", [0, 2])
def test_products_must_be_exactly_one(n):
    data = video()
    data["products"] = [{"product_ref": f"p0{i + 1}"} for i in range(n)]
    with pytest.raises(HandoffError, match=f"현재 {n}개"):
        validate_video(data)


def test_unknown_product_ref():
    with pytest.raises(HandoffError, match="p09"):
        validate_video(video(product_ref="p09"))


def test_null_product_ref_allowed():
    validate_video(video(product_ref=None))


def test_missing_evidence_field():
    with pytest.raises(HandoffError, match=r"evidences\[0\]"):
        validate_video(video(evidences=[{"text": "x"}]))


@pytest.mark.skipif(not NEM.exists(), reason="로컬 fixture 없음")
def test_nem_sample_matches_format():
    v = load_handoff(NEM)
    assert v["video_id"] == "ad_001"
    assert len(v["claims"]) == 23
