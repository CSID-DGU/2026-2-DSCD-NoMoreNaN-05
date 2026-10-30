import pytest

from claim_verification.clauses.disease_claims import (
    EXCEPTION_PENDING, LAW_PREVENTION, LAW_TREATMENT, NLI_UNAVAILABLE, DiseaseClaimCheck, fill)
from claim_verification.finding import UNCLEAR, VIOLATION
from claim_verification.nli import FakeNLI

PRODUCT = {"match": {"status": "not_found"}, "evi_product": None}


def scores(e):
    return {"entailment": e, "neutral": 1 - e, "contradiction": 0.0}


def nli_saying(prevent=0.0, treat=0.0):
    """가설에 '예방'/'걸리지'가 있으면 prevent, '치료'/'낫'이면 treat 점수."""
    def rule(premise, hypothesis):
        if "예방" in hypothesis or "걸리지" in hypothesis:
            return scores(prevent)
        if "치료" in hypothesis or "낫" in hypothesis:
            return scores(treat)
    return FakeNLI(rule=rule, model_id="fake-v0")


def run(text, nli):
    c = DiseaseClaimCheck(nli)
    claim = {"claim_id": "c01", "text": text}
    return c.prevention(claim, PRODUCT), c.treatment(claim, PRODUCT)


def test_no_disease_no_finding_and_no_nli_call():
    nli = nli_saying(prevent=0.99)
    assert run("피로 개선에 도움을 줄 수 있음", nli) == (None, None)
    assert nli.calls == []


def test_prevention_violation():
    ga, na = run("치매예방 뇌세포 보호", nli_saying(prevent=0.95, treat=0.1))
    assert (ga.status, ga.law_ref, ga.span) == (VIOLATION, LAW_PREVENTION, "치매")
    assert "fake-v0" in ga.detail
    assert na is None


def test_treatment_violation():
    ga, na = run("재발없이 방광염 완치해요", nli_saying(prevent=0.2, treat=0.9))
    assert ga is None
    assert (na.status, na.law_ref) == (VIOLATION, LAW_TREATMENT)


def test_middle_score_is_unclear():
    ga, _ = run("당뇨 걱정되는 분", nli_saying(prevent=0.5))
    assert ga.status == UNCLEAR


def test_risk_reduction_disease_waits_for_functionality_check():
    ga, _ = run("골다공증발생 위험 감소에 도움을 줌", nli_saying(prevent=0.9))
    assert (ga.status, ga.code) == (UNCLEAR, EXCEPTION_PENDING)


def test_risk_reduction_disease_treatment_has_no_exception():
    _, na = run("골다공증 치료", nli_saying(treat=0.9))
    assert na.status == VIOLATION


def test_without_nli_disease_claim_is_unclear():
    ga, na = run("감기예방 및 초기감기 치료", None)
    assert (ga.status, ga.code) == (UNCLEAR, NLI_UNAVAILABLE)
    assert (na.status, na.code) == (UNCLEAR, NLI_UNAVAILABLE)


def test_one_nli_call_per_claim():
    nli = nli_saying(prevent=0.9)
    run("감기예방 및 초기감기 치료", nli)
    assert len(nli.calls) == 1
    # 질병 1개(감기, 중복 제거) × 조항 2 × 가설 2
    assert len(nli.calls[0]) == 4


def test_best_disease_is_reported():
    def rule(p, h):
        return scores(0.9) if "성조숙증" in h and "예방" in h else scores(0.1)
    ga, _ = run("#소아비만예방 #성조숙증예방", FakeNLI(rule=rule))
    assert ga.span == "성조숙증"


@pytest.mark.parametrize("disease, expected", [
    ("감기", "이 문장은 감기를 예방할 수 있다고 주장한다."),
    ("골다공증", "이 문장은 골다공증을 예방할 수 있다고 주장한다."),
])
def test_fill_josa(disease, expected):
    assert fill("이 문장은 {d}{을} 예방할 수 있다고 주장한다.", disease) == expected


def test_fill_subject_josa():
    assert fill("{d}{이} 낫는다", "감기") == "감기가 낫는다"
    assert fill("{d}{이} 낫는다", "방광염") == "방광염이 낫는다"
