import json

from claim_verification.run import main

HANDOFF = {
    "video_id": "v1",
    "products": [{"product_ref": "p01", "product_name": "관절연골엔 난각막NEM"}],
    "claims": [{"claim_id": "c01", "product_ref": "p01", "text": "건강기능식품",
                "claim_type": "CERTIFICATION", "evidences": []}],
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
