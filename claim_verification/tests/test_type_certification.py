import pytest

from claim_verification.claim_types.checkers.certification import check_certification
from claim_verification.finding import SUPPORTED, UNCLEAR, VIOLATION

OUT_OF_SCOPE = "OUT_OF_SCOPE"


def product(**db):
    fields = {"STTEMNT_NO": "2004", "PRMS_DT": "20200101", "INDUTY_CD_NM": "건강기능식품전문제조업",
              "MAIN_FNCTN": "근력 개선에 도움을 줄 수 있음, 어린이 키성장에 도움을 줄 수 있음",
              "RAWMTRL_NM": "오미자추출물(제2018-9호), 비타민 C", "INDIV_RAWMTRL_NM": "오미자추출물(기능성원료인정제2018-9호)",
              "RAWMTRL_STD_INFO": [{"RCOGN_NO": "2018-9", "RAWMTRL_NM": "오미자추출물"}, {"RCOGN_NO": "", "RAWMTRL_NM": "비타민 C"}],
              "RAWMTRL_CLASS_INFO": []}
    fields.update(db)
    return {"DB": {"CERTIFICATION": fields}}


NO_NUMBER = dict(RAWMTRL_NM="비타민 C", INDIV_RAWMTRL_NM="비타민 C(고시형)", RAWMTRL_STD_INFO=[{"RCOGN_NO": "", "RAWMTRL_NM": "비타민 C"}])


def run(text, ingredients=(), prod=None):
    return check_certification({"text": text, "ingredients": list(ingredients)}, prod or product())


def codes(checks):
    return [(c.status, c.code) for c in checks]


@pytest.mark.parametrize("text", [
    "건강기능식품", "건강기능식품입니다.", "본 제품은 건강기능식품입니다.", "본 광고는 건강기능식품 광고입니다.", "* 건강기능식품입니다",
    "건강기능식품광고 / 광고심의필", "건강기능식품광고 | MAT-KR-2500100-v1.0-05/2025", "광고방송 / 건강기능식품", "하이뮨은 건강기능식품입니다",
    "건강기능식품 전품목 광고입니다", "건강기능식품 / 식품의약품안전처", "건강기능 식품입니다.",
])
def test_hff_label(text):
    assert codes(run(text)) == [(SUPPORTED, "HFF_ON_RECORD")]


@pytest.mark.parametrize("text,code", [
    ("광고심의필 : 230620068", "SOURCE_OR_REVIEW"),
    ("2504-PM-KR-CNT-25-00086", "SOURCE_OR_REVIEW"),
    ("출처 : Journal of Ethnopharmacology 87 (2003) 115-117", "SOURCE_OR_REVIEW"),
    ("건강기능식품 시장현황 및 소비자 실태조사, 한국건강기능식품협회", "SOURCE_OR_REVIEW"),
    ("* 구매율 1위 : 2024 칸타월드패널", "SALES_OR_RANK"),
    ("*칸타리서치 22년~24년 눈 건강 카테고리 구매량% 기준", "SALES_OR_RANK"),
    ("**2025년 12월 30일 데이팩 네이버 공식스토어기준", "SOURCE_OR_REVIEW"),
    ("세계일류상품", "OTHER_CERTIFICATION"),
    ("다양한 국제 인증을 통해 검증된 품질과 안전성", "OTHER_CERTIFICATION"),
    ("Effects of lutein. Investigative Ophthalmology & Visual Science, October 2011, Vol52, No.11", "SOURCE_OR_REVIEW"),
    ("특허 받은 난각막가수분해물 NEM®", "OTHER_CERTIFICATION"),
    ("Patent No. 10-2018-0069132", "OTHER_CERTIFICATION"),
    ("NON GMO", "OTHER_CERTIFICATION"),
    ("원료 안전성 미국 FDA NDI 등재", "OTHER_CERTIFICATION"),
    ("이탈리아 브이라벨이 인증한 비건 인증까지", "OTHER_CERTIFICATION"),
    ("해양수산부 신기술 인증 제 해양수산 신기술 -2024-0023호", "OTHER_CERTIFICATION"),
    ("통신판매업신고번호 : 2021-서울영등포-0512", "SOURCE_OR_REVIEW"),
    ("금속성 이물 검사 통과", "SOURCE_OR_REVIEW"),
    ("tvN <꽃보다할배 리턴즈> 중에서", "SOURCE_OR_REVIEW"),
    ("**기존 아이클리어 제품 라인업 기준", "SOURCE_OR_REVIEW"),
    ("• 21년 식약처 건강기능식품산업 주요 통계, 매출액 기준", "SALES_OR_RANK"),
    ("WINNER NUTRA INGREDIENTS USA AWARDS 2018", "OTHER_CERTIFICATION"),
    ("마야서트 인증 획득", "OTHER_CERTIFICATION"),
])
def test_out_of_scope(text, code):
    assert codes(run(text)) == [(OUT_OF_SCOPE, code)]


@pytest.mark.parametrize("text", ["*식약처 고시 기준", "2023년 10월 면역기능 개선과 피로개선에 도움 2종 기능성 인증 취득"])
def test_notice_and_domestic_certification_are_not_out_of_scope(text):
    assert OUT_OF_SCOPE not in {c.status for c in run(text)}


def test_star_note_with_recognition_number_is_checked():
    assert codes(run("*이중 기능성을 인정받은 루테인지아잔틴복합추출물 (제2018-4호) 기준"))[0][0] != OUT_OF_SCOPE


@pytest.mark.parametrize("text", ["GMP", "우수건강기능식품제조기준 GMP", "식약처 GMP인증 시설에서 생산"])
def test_gmp(text):
    assert codes(run(text)) == [(SUPPORTED, "GMP_BY_INDUSTRY")]


def test_gmp_needs_manufacturer():
    assert codes(run("GMP", prod=product(INDUTY_CD_NM="건강기능식품판매업"))) == [(UNCLEAR, "GMP_NOT_CONFIRMED")]


def test_recognition_number():
    assert codes(run("개별인정원료 제 2018-9호")) == [(SUPPORTED, "RECOGNITION_NO_MATCHES")]
    assert codes(run("오미자추출물(2018-09호)")) == [(SUPPORTED, "RECOGNITION_NO_MATCHES")]
    assert codes(run("개별인정원료 제 2015-16호")) == [(VIOLATION, "RECOGNITION_NO_MISMATCH")]


def test_first_claim_keeps_number_check_and_is_unclear():
    checks = run("국내 최초!* *이중 기능성을 인정받은 오미자추출물(제2018-9호) 기준")
    assert codes(checks) == [(SUPPORTED, "RECOGNITION_NO_MATCHES"), (UNCLEAR, "FIRST_CLAIM_UNPROVABLE")]


@pytest.mark.parametrize("text,ingredients,prod,status,code", [
    ("개별인정형 건강기능식품", (), None, SUPPORTED, "RECOGNITION_ON_PRODUCT"),
    ("개별인정형 건강기능식품", (), NO_NUMBER, VIOLATION, "RECOGNITION_ABSENT"),
    ("개별인정형 건강기능식품", (), dict(NO_NUMBER, RAWMTRL_CLASS_INFO=[{"MLSFC_NM": "개별인정형 건강기능식품"}]), UNCLEAR,
     "RECOGNITION_UNCONFIRMED"),
    ("오미자 추출물 식약처 개별인정", ("오미자 추출물",), None, SUPPORTED, "RECOGNITION_ON_PRODUCT"),
    ("루테인 식약처 개별인정", ("루테인",), None, UNCLEAR, "RECOGNITION_UNCONFIRMED"),
])
def test_individual_recognition(text, ingredients, prod, status, code):
    assert codes(run(text, ingredients, product(**prod) if prod else None)) == [(status, code)]


@pytest.mark.parametrize("text,status,code", [
    ("식약처 기능성 인정", SUPPORTED, "FUNCTION_ON_RECORD"),
    ("식약처 근력개선 기능성 인정", SUPPORTED, "FUNCTION_ON_RECORD"),
    ("키성장 기능성을 인정받은 원료", SUPPORTED, "FUNCTION_ON_RECORD"),
    ("식약처 혈당 기능성 인정", VIOLATION, "FUNCTION_NOT_ON_RECORD"),
    ("식약처에서 근력건강 기능성 인정", SUPPORTED, "FUNCTION_ON_RECORD"),
    ("식약처 혈압건강 기능성 인정", VIOLATION, "FUNCTION_NOT_ON_RECORD"),
    ("식약처 인정 6가지 기능성", UNCLEAR, "FUNCTION_NOT_CONFIRMED"),
    ("식약처에서 기능성을 인정받은 원료", SUPPORTED, "FUNCTION_ON_RECORD"),
])
def test_function_approved(text, status, code):
    assert codes(run(text)) == [(status, code)]


def test_first_with_function():
    assert codes(run("국내최초 식약처 근력개선 기능성 인정")) == [(UNCLEAR, "FIRST_CLAIM_UNPROVABLE"), (SUPPORTED, "FUNCTION_ON_RECORD")]


def test_functional_ingredient():
    assert codes(run("기능성 원료 오미자추출물", ("오미자추출물",))) == [(SUPPORTED, "FUNCTIONAL_INGREDIENT_ON_RECORD")]
    assert codes(run("기능성 원료 바나바잎 추출물", ("바나바잎 추출물",))) == [(VIOLATION, "FUNCTIONAL_INGREDIENT_ABSENT")]
    assert codes(run("기능성 원료는 오직 이 제품에만")) == [(UNCLEAR, "FUNCTION_NOT_CONFIRMED")]


def test_unclassified():
    assert codes(run("증명합니다 과학적으로")) == [(UNCLEAR, "CERTIFICATION_UNCLASSIFIED")]


def test_first_claim_with_date_note_is_not_out_of_scope():
    checks = run("국내최초 국내유일* 콜레스테롤 기능성 유산균 *2022년 8월 기준")
    assert codes(checks)[0] == (UNCLEAR, "FIRST_CLAIM_UNPROVABLE")
    assert {c.status for c in checks} == {UNCLEAR}


def test_first_individual_number_is_unclear():
    assert (UNCLEAR, "FIRST_CLAIM_UNPROVABLE") in codes(run("개별인정형 1호 건강기능식품 원료"))


def test_functional_ingredient_read_from_text_without_slot():
    assert codes(run("기능성 원료 오미자추출물")) == [(SUPPORTED, "FUNCTIONAL_INGREDIENT_ON_RECORD")]


def test_recognition_number_without_ho():
    assert codes(run("개별 인정형 기능성 원료 원료명 오미자추출물 인정번호 제2018-9")) == [(SUPPORTED, "RECOGNITION_NO_MATCHES")]
    assert codes(run("인정번호 제2006-17")) == [(VIOLATION, "RECOGNITION_NO_MISMATCH")]
    assert codes(run("Patent 2018-9")) == [(OUT_OF_SCOPE, "OTHER_CERTIFICATION")]


def test_function_phrase_is_read_not_adjective():
    checks = run("국내 최초 근력 개선에 도움을 줄 수 있는 기능성을 인정받은 원료로 만들었습니다")
    assert codes(checks) == [(UNCLEAR, "FIRST_CLAIM_UNPROVABLE"), (SUPPORTED, "FUNCTION_ON_RECORD")]
    assert codes(run("혈압 개선에 도움을 줄 수 있는 기능성을 인정받은 원료")) == [(VIOLATION, "FUNCTION_NOT_ON_RECORD")]


@pytest.mark.parametrize("text", ["인체에 유용한 기능성을 가진 원료를 사용하여 제조·가공한 건강기능식품입니다.",
                                  "유통기한 확인하여 식품선택 올바르게_건강기능 식품입니다."])
def test_hff_sentence_with_description(text):
    assert codes(run(text)) == [(SUPPORTED, "HFF_ON_RECORD")]


def test_described_first_claim_is_not_just_hff_label():
    assert codes(run("국내 최초 관절 건강기능식품입니다")) == [(UNCLEAR, "FIRST_CLAIM_UNPROVABLE"), (UNCLEAR, "FUNCTION_NOT_CONFIRMED")]


def test_direct_recognition_subject_is_unclear():
    assert codes(run("고려은단이 직접 개별 인정받은 좋은 원료.")) == [(UNCLEAR, "RECOGNITION_UNCONFIRMED")]


def test_number_prefixed_word_is_not_function_name():
    assert codes(run("피부개선 2중 기능성 인정")) == [(SUPPORTED, "FUNCTION_ON_RECORD")]


def test_intake_reference_is_not_function_claim():
    text = "건강기능식품 기능성 인정 일일섭취량, 루테인으로서 10~20mg/일"
    assert codes(run(text, ("루테인",))) == [(UNCLEAR, "FUNCTION_NOT_CONFIRMED")]


def test_hff_word_is_not_function_name():
    assert codes(run("건강기능식품 기능성 인정")) == [(SUPPORTED, "FUNCTION_ON_RECORD")]


MICROBE = dict(RAWMTRL_NM="회화나무열매추출물, Lactobacillus gasseri", INDIV_RAWMTRL_NM="Lactobacillus gasseri BNR17",
               MAIN_FNCTN="체지방 감소에 도움을 줄 수 있음", RAWMTRL_STD_INFO=[])


def test_first_claim_confirms_ingredient_and_function_but_stays_unclear():
    checks = run("국내 최초 체지방 감소 유산균", (), product(**MICROBE))
    assert codes(checks) == [(UNCLEAR, "FIRST_CLAIM_UNPROVABLE"), (SUPPORTED, "INGREDIENT_ON_RECORD"), (SUPPORTED, "FUNCTION_ON_RECORD")]
    assert [c.target for c in checks[1:]] == ["유산균", "체지방 감소"]


def test_first_claim_with_function_word_and_footnote():
    prod = product(RAWMTRL_NM="유산균복합물(제2022-15호)", INDIV_RAWMTRL_NM="", MAIN_FNCTN="혈중 콜레스테롤 개선", RAWMTRL_STD_INFO=[])
    assert [c.target for c in run("국내최초 국내유일* 콜레스테롤 기능성 유산균 *2022년 8월 기준", (), prod)[1:]] == ["유산균", "콜레스테롤"]


def test_first_claim_does_not_confirm_missing_parts():
    prod = product(**dict(MICROBE, RAWMTRL_NM="비타민 C", INDIV_RAWMTRL_NM="비타민 C"))
    assert codes(run("국내 최초 체지방 감소 유산균", (), prod))[1] == (UNCLEAR, "INGREDIENT_NOT_CONFIRMED")


def test_first_claim_checks_listed_ingredients():
    checks = run("국내최초 식약처 기능성 인정 오미자추출물 쉬잔드린 함유", ("오미자추출물", "쉬잔드린"))
    assert {(c.target, c.code) for c in checks if c.target} == {("오미자추출물", "INGREDIENT_ON_RECORD"), ("쉬잔드린", "INGREDIENT_NOT_CONFIRMED")}
