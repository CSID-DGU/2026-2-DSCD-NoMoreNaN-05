import json

from claim_verification.run import main

HANDOFF = {
    "video_id": "v1",
    "db_version": "2026-09-20T09:51:18Z",
    "product": {"match": {"status": "not_found", "method": None, "note": None},
                "evi_product": None},
    "claims": [{"claim_id": "c01", "text": "건강기능식품", "claim_type": "CERTIFICATION"}],
}


def test_writes_result_file(tmp_path, capsys):
    src, dst = tmp_path / "h.json", tmp_path / "r.json"
    src.write_text(json.dumps(HANDOFF, ensure_ascii=False), encoding="utf-8")
    assert main([str(src), str(dst)]) == 0
    result = json.loads(dst.read_text(encoding="utf-8"))
    assert result["video_id"] == "v1"
    assert result["claims"][0]["label"] == "OUT_OF_SCOPE"
    assert "v1 CHECKED" in capsys.readouterr().err


def test_wrong_args_shows_usage(capsys):
    assert main([]) == 2
    assert "python -m claim_verification.run" in capsys.readouterr().err
