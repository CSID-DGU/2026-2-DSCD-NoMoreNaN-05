import pytest

from claim_verification.finding import SUPPORTED, Finding


def test_to_dict_has_all_fields():
    f = Finding(SUPPORTED, "CERT", "4호 마", "건강기능식품", "건강기능식품으로 등록된 제품")
    assert f.to_dict() == {
        "status": "SUPPORTED", "code": "CERT", "law_ref": "4호 마",
        "span": "건강기능식품", "detail": "건강기능식품으로 등록된 제품", "evidence": [],
    }


def test_unknown_status_rejected():
    with pytest.raises(ValueError, match="PASS"):
        Finding("PASS", "CERT", "4호 마", "", "")

