import pytest

from claim_verification.scripts.select_videos import select, usable_claims


def _video(video_id, usable=0, other=0):
    claims = [{"claim_id": f"c{i}", "product_ref": "p01", "claim_type": "EFFECT"} for i in range(usable)]
    claims += [{"claim_id": f"e{i}", "product_ref": "p01", "claim_type": "ETC"} for i in range(other)]
    return {"video_id": video_id, "products": [{"product_ref": "p01", "product_name": "제품"}], "claims": claims}


def test_usable_claims_needs_named_product_and_objective_type():
    video = _video("v", usable=2, other=1)
    assert usable_claims(video) == 2
    video["products"][0]["product_name"] = None
    assert usable_claims(video) == 0


def test_select_removes_least_usable_and_keeps_order():
    videos = [_video("a", usable=3), _video("b", usable=0, other=2), _video("c", usable=0), _video("d", usable=1)]
    kept, removed = select(videos, 2)
    assert [v["video_id"] for v in removed] == ["c", "b"]
    assert [v["video_id"] for v in kept] == ["a", "d"]


def test_select_ignores_match_status():
    video = _video("a", usable=1)
    other = _video("b", usable=1)
    video["products"][0]["match"] = {"status": "confirmed"}
    other["products"][0]["match"] = {"status": "not_found"}
    assert select([video, other], 1)[1] == [video]


def test_select_rejects_too_many():
    with pytest.raises(ValueError):
        select([_video("a")], 2)
