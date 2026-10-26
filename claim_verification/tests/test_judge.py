from claim_verification.finding import OVERCLAIM, SUPPORTED, UNCLEAR, VIOLATION, Finding
from claim_verification.judge import CHECKED, NO_CLAIMS, OUT_OF_SCOPE, judge_video, label

PRODUCT = {"product_ref": "p01", "product_name": "관절연골엔 난각막NEM"}


def f(status):
    return Finding(status, "TEST", "테스트", "", "")


def video(*claims):
    return {"video_id": "v1", "products": [PRODUCT], "claims": list(claims)}


def claim(cid, text, product_ref="p01"):
    return {"claim_id": cid, "product_ref": product_ref, "text": text,
            "claim_type": "ETC", "evidences": [{"source_ref": "x", "text": "y", "source": {}}]}


def test_label_order():
    assert label([f(SUPPORTED), f(VIOLATION)]) == VIOLATION
    assert label([f(SUPPORTED), f(UNCLEAR), f(OVERCLAIM)]) == OVERCLAIM
    assert label([f(SUPPORTED), f(UNCLEAR)]) == UNCLEAR
    assert label([f(SUPPORTED)]) == SUPPORTED
    assert label([]) == OUT_OF_SCOPE


def test_no_checks_means_out_of_scope():
    result = judge_video(video(claim("c01", "건강기능식품")), checks=[])
    assert result["status"] == CHECKED
    assert result["claims"][0]["label"] == OUT_OF_SCOPE
    assert result["claims"][0]["findings"] == []


def test_no_claims():
    assert judge_video(video(), checks=[])["status"] == NO_CLAIMS


def test_every_check_runs_on_every_claim():
    def only_cert(c, p):
        return f(SUPPORTED) if "건강기능식품" in c["text"] else None

    def always_unclear(c, p):
        return f(UNCLEAR)

    out = judge_video(video(claim("c01", "건강기능식품"), claim("c02", "제조원")),
                      checks=[only_cert, always_unclear])
    assert [c["label"] for c in out["claims"]] == [UNCLEAR, UNCLEAR]
    assert len(out["claims"][0]["findings"]) == 2
    assert len(out["claims"][1]["findings"]) == 1


def test_null_product_ref_gets_video_product():
    seen = []
    judge_video(video(claim("c01", "세계판매 1위", product_ref=None)),
                checks=[lambda c, p: seen.append(p) or None])
    assert seen == [PRODUCT]


def test_output_passes_claim_fields_and_drops_evidences():
    out = judge_video(video(claim("c01", "건강기능식품")), checks=[])["claims"][0]
    assert out["claim_type"] == "ETC"
    assert "evidences" not in out
