import pytest

from claim_verification.diseases import find


def terms(text, **kw):
    return [f["term"] for f in find(text, **kw)]


@pytest.mark.parametrize("text, expected", [
    ("감기예방 및 초기감기 치료", ["감기", "감기"]),
    ("#소아비만예방 #성조숙증예방", ["비만", "성조숙증"]),     # 해시태그
    ("다낭성난소증후군 예방", ["다낭성난소증후군"]),             # Kiwi가 나눈 명사를 다시 붙임
    ("이명 마늘 강황 비타민C 천연 귀울림 감소 지원", ["이명", "귀울림"]),  # 사용자 단어 등록
])
def test_finds_disease(text, expected):
    assert terms(text) == expected


@pytest.mark.parametrize("text", [
    "제조원 : 콜마비앤에이치(주)음성공장",   # 회사 이름 속 "마비"
    "배우 최수종, 고두심",                   # 사람 이름 속 "수종"
    "식약처 건강기능식품 산업주요통계",       # 단어 경계를 넘는 "요통"
    "프로바이오틱스 유산균",
])
def test_ignores_letters_inside_other_words(text):
    assert terms(text) == []


def test_partial_inside_common_noun():
    found = find("암세포를 없애 항암하는게 핵심입니다")
    assert [(f["term"], f["partial"]) for f in found] == [("암", True), ("암", True)]


def test_symptom_only_when_asked():
    assert terms("두근거림이 사라져요") == []
    assert terms("두근거림이 사라져요", kinds=("symptom",)) == ["두근거림"]


def test_span_points_into_text():
    text = "치매예방 뇌세포 보호"
    f = find(text)[0]
    assert text[f["start"]:f["end"]] == "치매"


@pytest.mark.parametrize("text", [
    "카르복시메틸셀룰로스",
    "스테아린산마그네슘 카르복시메틸셀룰로스 사이클로덱스트린",
])
def test_partial_needs_common_noun_rest(text):
    assert terms(text) == []
