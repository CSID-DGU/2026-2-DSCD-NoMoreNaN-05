import pytest

from claim_verification.evaluation.join import JoinError, join


def _gold(*claims):
    return [{"video_id": "v1", "claims": [{"claim_id": cid, "product_ref": "p01", "gold_label": label}
                                          for cid, label in claims]}]


def _result(cid, label, ref="p01"):
    return {"video_id": "v1", "product_ref": ref, "claim_id": cid, "claim_type": ["EFFECT"], "text": "문장",
            "final_label": label, "decided_by": ["B"], "A": None, "B": {"label": label}}


def test_join_pairs_gold_and_pred_in_result_order():
    rows = join([_result("c02", "UNCLEAR"), _result("c01", "SUPPORTED")], _gold(("c01", "SUPPORTED"), ("c02", "OVERCLAIM")))
    assert [(r["claim_id"], r["gold"], r["pred"]) for r in rows] == [("c02", "OVERCLAIM", "UNCLEAR"), ("c01", "SUPPORTED", "SUPPORTED")]
    assert rows[0]["decided_by"] == ["B"]


def test_result_missing_from_gold_is_error():
    with pytest.raises(JoinError, match="정답에 없는"):
        join([_result("c01", "SUPPORTED", ref="p02")], _gold(("c01", "SUPPORTED")))


def test_gold_missing_from_results_is_error():
    with pytest.raises(JoinError, match="최종 결과에 없는 클레임 1건"):
        join([_result("c01", "SUPPORTED")], _gold(("c01", "SUPPORTED"), ("c02", "UNCLEAR")))


def test_duplicates_and_missing_label_are_errors():
    with pytest.raises(JoinError, match="최종 결과 키 중복"):
        join([_result("c01", "SUPPORTED"), _result("c01", "UNCLEAR")], _gold(("c01", "SUPPORTED")))
    gold = _gold(("c01", "SUPPORTED"))
    del gold[0]["claims"][0]["gold_label"]
    with pytest.raises(JoinError, match="정답 라벨 없음"):
        join([_result("c01", "SUPPORTED")], gold)


def test_join_keeps_skipped_reason():
    result = {**_result("c01", "UNCLEAR"), "A": None, "B": None, "skipped_reason": "PRODUCT_NOT_FOUND"}
    assert join([result], _gold(("c01", "UNCLEAR")))[0]["skipped_reason"] == "PRODUCT_NOT_FOUND"
