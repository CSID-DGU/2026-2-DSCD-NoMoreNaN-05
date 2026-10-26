import pytest

from claim_verification.finding import SUPPORTED, Finding, cite


def test_to_dict_has_all_fields():
    f = Finding(SUPPORTED, "CERT", "4호 마", "건강기능식품", "건강기능식품으로 등록된 제품")
    assert f.to_dict() == {
        "status": "SUPPORTED", "code": "CERT", "law_ref": "4호 마",
        "span": "건강기능식품", "detail": "건강기능식품으로 등록된 제품", "evidence": [],
    }


def test_unknown_status_rejected():
    with pytest.raises(ValueError, match="PASS"):
        Finding("PASS", "CERT", "4호 마", "", "")


def test_cite_keeps_only_source_ref_and_text():
    ev = {"source_ref": "product:6411:company_name", "text": "(주)서흥",
          "source": {"table": "products"}, "similarity": 0.89}
    assert cite(ev) == {"source_ref": "product:6411:company_name", "text": "(주)서흥"}
