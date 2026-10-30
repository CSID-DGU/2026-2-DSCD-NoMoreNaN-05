from claim_verification.finding import OVERCLAIM, SUPPORTED, UNCLEAR, VIOLATION, Finding
from claim_verification.judge import CHECKED, NO_CLAIMS, OUT_OF_SCOPE, judge_video, label

PRODUCT = {"match": {"status": "confirmed", "method": "report_number", "note": None},
           "evi_product": {"product_id": 6411, "main_functionality": "관절 및 연골 건강에 도움을 줄 수 있음"}}


def f(status):
    return Finding(status, "TEST", "테스트", "", "")


def video(*claims):
    return {"video_id": "v1", "db_version": "2026-09-20T09:51:18Z",
            "product": PRODUCT, "claims": list(claims)}


def claim(cid, text):
    return {"claim_id": cid, "text": text, "claim_type": "ETC", "effect": "x"}


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


def test_every_claim_gets_video_product():
    seen = []
    judge_video(video(claim("c01", "세계판매 1위"), claim("c02", "제조원")),
                checks=[lambda c, p: seen.append(p) or None])
    assert seen == [PRODUCT, PRODUCT]


def test_output_passes_claim_fields_only():
    result = judge_video(video(claim("c01", "건강기능식품")), checks=[])
    assert result["db_version"] == "2026-09-20T09:51:18Z"
    assert result["product"] == PRODUCT
    out = result["claims"][0]
    assert out["claim_type"] == "ETC"
    assert "effect" not in out


def test_disclaimer_skips_checks():
    calls = []
    out = judge_video(video(claim("c01", "본 제품은 질병의 예방 및 치료를 위한 의약품이 아닙니다.")),
                      checks=[lambda c, p: calls.append(c) or f(VIOLATION)])
    assert out["claims"][0]["label"] == "DISCLAIMER"
    assert out["claims"][0]["findings"] == []
    assert calls == []

