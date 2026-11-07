import json

import pytest

from claim_verification.final.merge import MergeError, final_label, merge, video_info
from claim_verification.final.run import main


def _claim(cid, claim_type, text="문장", ref="p01"):
    return {"claim_id": cid, "product_ref": ref, "text": text, "claim_type": claim_type}


def _video(claims, status="confirmed"):
    product = {"product_ref": "p01", "product_name": "제품", "match": {"status": status}, "DB": {}}
    return {"video_id": "v1", "products": [product], "claims": claims}


def _a(claims=(), skipped=()):
    return {"video_id": "v1", "claims": list(claims), "skipped": list(skipped)}


def _a_claim(cid, label, codes=("C",)):
    return {"claim_id": cid, "label": label, "reason_codes": list(codes)}


def _b(cid, label, ref="p01"):
    return {"video_id": "v1", "product_ref": ref, "claim_id": cid, "label": label, "reason_code": "R"}


@pytest.mark.parametrize("a,b,expected", [
    ("SUPPORTED", "OVERCLAIM", ("OVERCLAIM", ["B"])),
    ("VIOLATION", "OVERCLAIM", ("VIOLATION", ["A"])),
    ("UNCLEAR", "UNCLEAR", ("UNCLEAR", ["A", "B"])),
    ("OUT_OF_SCOPE", "SUPPORTED", ("SUPPORTED", ["B"])),
    ("DISCLAIMER", "VIOLATION", ("DISCLAIMER", ["A"])),
    ("VIOLATION", "DISCLAIMER", ("DISCLAIMER", ["B"])),
    ("DISCLAIMER", "DISCLAIMER", ("DISCLAIMER", ["A", "B"])),
    (None, "SUPPORTED", ("SUPPORTED", ["B"])),
    ("UNCLEAR", None, ("UNCLEAR", ["A"])),
])
def test_final_label_order(a, b, expected):
    assert final_label(a, b) == expected


def test_merge_keeps_input_order_and_parts():
    video = _video([_claim("c01", ["QUANTITY"]), _claim("c02", ["EFFECT", "COMPOSITION"]), _claim("c03", "EFFECT")])
    a = _a([_a_claim("c01", "SUPPORTED"), _a_claim("c02", "UNCLEAR")])
    rows = merge([video], [a], [_b("c02", "SUPPORTED"), _b("c03", "OVERCLAIM")])
    assert [(r["claim_id"], r["final_label"], r["decided_by"]) for r in rows] == [
        ("c01", "SUPPORTED", ["A"]), ("c02", "UNCLEAR", ["A"]), ("c03", "OVERCLAIM", ["B"])]
    assert rows[0]["B"] is None and rows[2]["A"] is None
    assert rows[1]["claim_type"] == ["EFFECT", "COMPOSITION"]


def test_effect_without_b_result_is_error():
    with pytest.raises(MergeError, match="B 결과가 없음"):
        merge([_video([_claim("c01", ["EFFECT", "ETC"])])], [_a()], [])


def test_b_result_for_non_effect_is_error():
    with pytest.raises(MergeError, match="EFFECT가 없는"):
        merge([_video([_claim("c01", "QUANTITY")])], [_a([_a_claim("c01", "SUPPORTED")])], [_b("c01", "SUPPORTED")])


def test_b_result_not_in_input_is_error():
    with pytest.raises(MergeError, match="입력에 없는"):
        merge([_video([])], [_a()], [_b("c09", "SUPPORTED")])


def test_duplicate_or_unknown_b_is_error():
    with pytest.raises(MergeError, match="중복"):
        merge([_video([])], [_a()], [_b("c01", "SUPPORTED"), _b("c01", "UNCLEAR")])
    with pytest.raises(MergeError, match="알 수 없는"):
        merge([_video([])], [_a()], [_b("c01", "MAYBE")])


def test_skipped_claim_is_unclear_with_reason():
    video = _video([_claim("c01", "EFFECT")])
    rows = merge([video], [_a(skipped=[{"claim_id": "c01", "reason": "PRODUCT_NOT_FOUND"}])], [])
    assert rows[0]["final_label"] == "UNCLEAR"
    assert rows[0]["skipped_reason"] == "PRODUCT_NOT_FOUND"


def test_main_runs_a_and_writes_final_file(tmp_path):
    claims = [_claim("c01", ["ETC"]), _claim("c02", "EFFECT"), {**_claim("c03", "PERSON_CREDENTIAL"), "gold_label": "X"}]
    source, b_path = tmp_path / "in.json", tmp_path / "b.json"
    source.write_text(json.dumps([_video(claims)], ensure_ascii=False), encoding="utf-8")
    b_path.write_text(json.dumps({"results": [_b("c02", "OVERCLAIM")]}), encoding="utf-8")
    assert main([str(source), str(b_path), str(tmp_path / "out"), "nli-verification@abc"]) == 0
    final = json.loads((tmp_path / "out" / "final_results.json").read_text(encoding="utf-8"))
    assert final["meta"]["b_source"] == "nli-verification@abc"
    assert [r["final_label"] for r in final["results"]] == ["OUT_OF_SCOPE", "OVERCLAIM", "OUT_OF_SCOPE"]
    summary = json.loads((tmp_path / "out" / "final_summary.json").read_text(encoding="utf-8"))
    assert summary["labels"] == {"OVERCLAIM": 1, "OUT_OF_SCOPE": 2}


def test_row_keeps_a_checks():
    check = {"claim_type": "COMPOSITION", "status": "VIOLATION", "code": "INGREDIENT_ABSENT", "reason": "없음",
             "target": "비타민C", "claim_value": "비타민C", "evidence": [{"field": "RAWMTRL_NM", "value": "녹차추출물"}]}
    a = _a([{**_a_claim("c01", "VIOLATION"), "checks": [check]}])
    row = merge([_video([_claim("c01", "COMPOSITION")])], [a], [])[0]
    assert row["A"]["checks"] == [check]
    row = merge([_video([_claim("c01", "QUANTITY")])], [_a([_a_claim("c01", "SUPPORTED")])], [])[0]
    assert row["A"]["checks"] == []


def test_row_keeps_parsed_fields_and_time():
    claim = {**_claim("c01", "COMPOSITION"), "ingredients": ["비타민C"], "t_start": 41.0, "t_end": 45.0}
    row = merge([_video([claim])], [_a([_a_claim("c01", "SUPPORTED")])], [])[0]
    assert row["parsed"]["ingredients"] == ["비타민C"] and row["parsed"]["quantity"] is None
    assert (row["t_start"], row["t_end"]) == (41.0, 45.0)


def test_row_time_is_null_when_input_has_none():
    row = merge([_video([_claim("c01", "QUANTITY")])], [_a([_a_claim("c01", "SUPPORTED")])], [])[0]
    assert row["t_start"] is None and row["t_end"] is None


def test_main_writes_product_official_info_once_per_video(tmp_path):
    video = {**_video([_claim("c01", ["ETC"])]), "url": "https://youtu.be/x"}
    video["products"][0].update(manufacturing_report_number="2013", DB={"COMPOSITION": {"RAWMTRL_NM": "녹차추출물"}})
    source, b_path = tmp_path / "in.json", tmp_path / "b.json"
    source.write_text(json.dumps([video], ensure_ascii=False), encoding="utf-8")
    b_path.write_text("[]", encoding="utf-8")
    assert main([str(source), str(b_path), str(tmp_path / "out")]) == 0
    final = json.loads((tmp_path / "out" / "final_results.json").read_text(encoding="utf-8"))
    [v] = final["videos"]
    assert v["video_id"] == "v1" and v["url"] == "https://youtu.be/x"
    [p] = v["products"]
    assert p["manufacturing_report_number"] == "2013" and p["match_status"] == "confirmed"
    assert p["DB"]["COMPOSITION"]["RAWMTRL_NM"] == "녹차추출물"
    assert v["summary"] == {"claims": 1, "labels": {"OUT_OF_SCOPE": 1}}


def test_video_summary_counts_only_that_video_in_label_order():
    v1 = _video([_claim("c01", "QUANTITY"), _claim("c02", "QUANTITY"), _claim("c03", "QUANTITY")])
    v2 = {**_video([_claim("c01", "QUANTITY")]), "video_id": "v2"}
    a1 = _a([_a_claim("c01", "SUPPORTED"), _a_claim("c02", "UNCLEAR"), _a_claim("c03", "SUPPORTED")])
    a2 = {**_a([_a_claim("c01", "VIOLATION")]), "video_id": "v2"}
    rows = merge([v1, v2], [a1, a2], [])
    s1 = video_info(v1, rows)["summary"]
    assert s1 == {"claims": 3, "labels": {"UNCLEAR": 1, "SUPPORTED": 2}}
    assert list(s1["labels"]) == ["UNCLEAR", "SUPPORTED"]
    assert video_info(v2, rows)["summary"] == {"claims": 1, "labels": {"VIOLATION": 1}}
