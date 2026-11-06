import json

from claim_verification.evaluation.run import main, report


def _row(cid, gold, pred, a=None, b=None, claim_type=("EFFECT",)):
    return {"video_id": "v1", "product_ref": "p01", "claim_id": cid, "claim_type": list(claim_type), "text": "문장",
            "gold": gold, "pred": pred, "decided_by": [],
            "A": {"label": a, "reason_codes": []} if a else None, "B": {"label": b} if b else None}


def test_report_sections():
    rows = [_row("c01", "SUPPORTED", "SUPPORTED", b="SUPPORTED"),
            _row("c02", "UNCLEAR", "UNCLEAR", a="UNCLEAR", b="SUPPORTED", claim_type=("EFFECT", "QUANTITY")),
            _row("c03", "SUPPORTED", "UNCLEAR", a="UNCLEAR", b="SUPPORTED", claim_type=("EFFECT", "QUANTITY")),
            _row("c04", "VIOLATION", "VIOLATION", a="VIOLATION", claim_type=("QUANTITY",))]
    rep = report(rows)
    assert rep["overall"]["n"] == 4 and rep["overall"]["accuracy"] == 0.75
    assert {k: m["n"] for k, m in rep["by_source"].items()} == {"A·B": 2, "B만": 1, "A만": 1}
    assert rep["by_claim_type"]["EFFECT+QUANTITY"]["n"] == 2
    assert rep["b_only_label"]["n"] == 3 and rep["b_only_label"]["accuracy"] == 2 / 3
    assert rep["a_only_label"]["accuracy"] == 2 / 3
    assert rep["merge_changes"] == {"n": 2, "outcome": {"틀림→맞음": 1, "맞음→틀림": 1},
                                    "transitions": {"SUPPORTED→UNCLEAR": 2}}


def test_main_writes_reports(tmp_path):
    final = {"meta": {"b_source": "nli@abc"},
             "results": [{"video_id": "v1", "product_ref": "p01", "claim_id": "c01", "claim_type": ["EFFECT"], "text": "문장",
                          "final_label": "OVERCLAIM", "decided_by": ["B"], "A": None, "B": {"label": "OVERCLAIM"}},
                         {"video_id": "v1", "product_ref": "p01", "claim_id": "c02", "claim_type": ["QUANTITY"], "text": "문장",
                          "final_label": "SUPPORTED", "decided_by": ["A"], "A": {"label": "SUPPORTED", "reason_codes": []}, "B": None}]}
    gold = [{"video_id": "v1", "claims": [{"claim_id": "c01", "product_ref": "p01", "gold_label": "OVERCLAIM"},
                                          {"claim_id": "c02", "product_ref": "p01", "gold_label": "UNCLEAR"}]}]
    (tmp_path / "final.json").write_text(json.dumps(final, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "gold.json").write_text(json.dumps(gold, ensure_ascii=False), encoding="utf-8")
    assert main([str(tmp_path / "final.json"), str(tmp_path / "gold.json"), str(tmp_path / "out")]) == 0
    rep = json.loads((tmp_path / "out" / "eval_report.json").read_text(encoding="utf-8"))
    assert rep["overall"]["accuracy"] == 0.5 and rep["meta"]["b_source"] == "nli@abc"
    assert [e["claim_id"] for e in json.loads((tmp_path / "out" / "eval_errors.json").read_text(encoding="utf-8"))] == ["c02"]
    assert "정확도 **50.0%**" in (tmp_path / "out" / "eval_report.md").read_text(encoding="utf-8")


def test_wrong_arguments():
    assert main([]) == 2
