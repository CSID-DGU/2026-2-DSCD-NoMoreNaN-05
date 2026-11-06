import pytest

from claim_verification.scripts.select_videos import missing_refs, select, usable_claims


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


def test_select_by_ref_removes_most_missing_refs_first():
    many = _video("a", usable=5)
    many["claims"] += [{"claim_id": "n1", "product_ref": None, "claim_type": "EFFECT"},
                       {"claim_id": "n2", "product_ref": None, "claim_type": "QUANTITY"}]
    etc_only = _video("b", usable=5)
    etc_only["claims"].append({"claim_id": "n3", "product_ref": None, "claim_type": "ETC"})
    empty = _video("c")
    assert [v["video_id"] for v in select([many, etc_only, empty], 2, by_ref=True)[1]] == ["a"]
    assert [v["video_id"] for v in select([many, etc_only, empty], 2)[1]] == ["c"]


def test_list_claim_type_counts_when_any_type_is_objective():
    video = _video("v")
    video["claims"] = [{"claim_id": "c1", "product_ref": "p01", "claim_type": ["ETC", "QUANTITY"]},
                       {"claim_id": "c2", "product_ref": "p01", "claim_type": ["PERSON_CREDENTIAL", "ETC"]},
                       {"claim_id": "c3", "product_ref": None, "claim_type": ["ETC"]},
                       {"claim_id": "c4", "product_ref": None, "claim_type": ["PERSON_CREDENTIAL"]}]
    assert usable_claims(video) == 1
    assert missing_refs(video) == 1


def test_select_rejects_too_many():
    with pytest.raises(ValueError):
        select([_video("a")], 2)
