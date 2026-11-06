import json

import pytest

from claim_verification.claim_types.judge import judge_video
from claim_verification.inputs import InputError
from claim_verification.claim_types.run import load_videos, main, summarize


def _video():
    product = {"product_ref": "p01", "product_name": "제품", "manufacturing_report_number": "1",
               "match": {"status": "confirmed"}, "DB": {}}
    missing = {"product_ref": "p02", "product_name": "없음", "manufacturing_report_number": None,
               "match": {"status": "not_found"}, "DB": None}
    claims = [
        {"claim_id": "c01", "product_ref": "p01", "text": "홍보 문구", "claim_type": "ETC"},
        {"claim_id": "c02", "product_ref": "p01", "text": "관절 건강", "claim_type": "EFFECT"},
        {"claim_id": "c03", "product_ref": "p01", "text": "본 제품은 의약품이 아닙니다.", "claim_type": "EFFECT"},
        {"claim_id": "c04", "product_ref": "p02", "text": "눈 건강", "claim_type": "EFFECT"},
    ]
    return {"video_id": "v1", "db_version": "x", "products": [product, missing], "claims": claims}


def test_summary_counts():
    video = _video()
    summary = summarize([video], [judge_video(video)])
    assert summary["claims"] == 4
    assert summary["judged"] == 2
    assert summary["for_b"] == 1
    assert summary["skipped"] == {"PRODUCT_NOT_FOUND": 1}
    assert summary["labels"] == {"EFFECT": {"DISCLAIMER": 1}, "ETC": {"OUT_OF_SCOPE": 1}}
    assert summary["reason_codes"]["OUT_OF_SCOPE"] == {"NOT_A_CLAIM": 1}


def test_multi_type_labels_are_keyed_by_combination():
    video = _video()
    video["claims"] = [{"claim_id": "c01", "product_ref": "p01", "text": "모델 추천", "claim_type": ["PERSON_CREDENTIAL", "ETC"]}]
    assert summarize([video], [judge_video(video)])["labels"] == {"PERSON_CREDENTIAL+ETC": {"OUT_OF_SCOPE": 1}}


def test_gold_label_is_removed_before_judging(tmp_path, capsys):
    video = _video()
    video["claims"][0]["gold_label"] = "SUPPORTED"
    source = tmp_path / "in.json"
    source.write_text(json.dumps([video], ensure_ascii=False), encoding="utf-8")
    assert main([str(source), str(tmp_path / "out")]) == 0
    assert "gold_label 1건" in capsys.readouterr().err
    assert "gold_label" not in (tmp_path / "out" / "results.json").read_text(encoding="utf-8")


def test_main_writes_results_and_summary(tmp_path):
    source = tmp_path / "in.json"
    source.write_text(json.dumps([_video()], ensure_ascii=False), encoding="utf-8")
    assert main([str(source), str(tmp_path / "out")]) == 0
    assert json.loads((tmp_path / "out" / "summary.json").read_text(encoding="utf-8"))["videos"] == 1
    assert json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))[0]["video_id"] == "v1"


def test_load_videos_from_folder(tmp_path):
    (tmp_path / "v1.json").write_text(json.dumps(_video(), ensure_ascii=False), encoding="utf-8")
    assert [v["video_id"] for v in load_videos(tmp_path)] == ["v1"]


def test_load_videos_checks_format(tmp_path):
    video = _video()
    video["products"][0]["match"]["status"] = "matched"
    source = tmp_path / "in.json"
    source.write_text(json.dumps([video], ensure_ascii=False), encoding="utf-8")
    with pytest.raises(InputError, match="알 수 없는 status"):
        load_videos(source)


def test_wrong_arguments():
    assert main([]) == 2
