from pathlib import Path

import pytest

from claim_verification.inputs import HandoffError, load_handoff, validate_video

# NEM 견본을 1차 형식으로 옮긴 것. 로컬에만 있다.
SAMPLE = Path(__file__).resolve().parents[2] / "data/fixtures/handoff_v1_ad_001.json"

EVI = {"product_id": 6411, "product_name": "관절연골엔 난각막NEM",
       "main_functionality": "관절 및 연골 건강에 도움을 줄 수 있음"}


def video(status="confirmed", evi=EVI, **claim_overrides):
    claim = {"claim_id": "c01", "text": "건강기능식품"}
    claim.update(claim_overrides)
    return {"video_id": "v1", "db_version": "2026-09-20T09:51:18Z",
            "product": {"match": {"status": status, "method": None, "note": None},
                        "evi_product": evi},
            "claims": [claim]}


def test_valid_video_passes():
    validate_video(video())


@pytest.mark.parametrize("status", ["confirmed", "unresolved"])
def test_found_product_needs_main_functionality(status):
    with pytest.raises(HandoffError, match=r"evi_product: 필드 없음 \['main_functionality'\]"):
        validate_video(video(status=status, evi={"product_id": 6411}))


def test_found_product_needs_evi_product():
    with pytest.raises(HandoffError, match="unresolved인데 evi_product가 없음"):
        validate_video(video(status="unresolved", evi=None))


def test_not_found_has_no_evi_product():
    validate_video(video(status="not_found", evi=None))
    with pytest.raises(HandoffError, match="not_found인데 evi_product가 있음"):
        validate_video(video(status="not_found"))


def test_unknown_match_status():
    with pytest.raises(HandoffError, match="알 수 없는 status 'unresolved_manufacturer_conflict'"):
        validate_video(video(status="unresolved_manufacturer_conflict"))


def test_missing_claim_field_names_location():
    data = video()
    del data["claims"][0]["text"]
    with pytest.raises(HandoffError, match="v1/c01"):
        validate_video(data)


def test_db_version_not_required():
    data = video()
    del data["db_version"]
    validate_video(data)


@pytest.mark.skipif(not SAMPLE.exists(), reason="로컬 fixture 없음")
def test_sample_matches_format():
    v = load_handoff(SAMPLE)
    assert v["video_id"] == "ad_001"
    assert v["product"]["match"]["status"] == "unresolved"
    assert "골다공증" in v["product"]["evi_product"]["main_functionality"]
    assert len(v["claims"]) == 23
