import pytest

from claim_verification.claim_types.checkers.composition import make_check_composition
from claim_verification.claim_types.parsing.lexicon import Lexicon
from claim_verification.claim_types.parsing.nutrients import part_names
from claim_verification.finding import SUPPORTED, UNCLEAR, VIOLATION

LEXICON = Lexicon({"아연": ["아연"], "칼슘": ["칼슘"], "루테인": ["루테인"], "lutein": ["루테인"], "콜라겐": ["콜라겐"],
                   "우유": ["락토페린"], "대두": ["가", "나"], "셀레늄": ["셀레늄"], "히알루론산": ["히알루론산"]})
check = make_check_composition(LEXICON)


def product(**db):
    fields = {"RAWMTRL_NM": "비타민 C, 프로바이오틱스", "INDIV_RAWMTRL_NM": "비타민 C(고시형), 밀크씨슬(카르두스 마리아누스) 추출물(고시형)",
              "ETC_RAWMTRL_NM": "홍삼농축액, 비타민B12혼합제제, 해조칼슘", "CAP_RAWMTRL_NM": "", "PRDLST_CDNM": "", "SUNGSANG": "갈색의 연질캡슐",
              "BASE_STANDARD": "2) 엠에스엠(MSM) : 표시량(300 mg/500 mg)의 80~120%", "RAWMTRL_DICT_INFO": []}
    fields.update(db)
    return {"DB": {"COMPOSITION": fields}}


def run(text, ingredients, prod=None):
    return check({"text": text, "ingredients": list(ingredients)}, prod or product())


def codes(checks):
    return [(c.status, c.code) for c in checks]


@pytest.mark.parametrize("name,status,code", [
    ("비타민C", SUPPORTED, "INGREDIENT_FOUND"),
    ("VITAMIN C", SUPPORTED, "INGREDIENT_FOUND"),
    ("밀크씨슬 추출물", SUPPORTED, "INGREDIENT_FOUND"),
    ("밀크씨슬추출물", SUPPORTED, "INGREDIENT_FOUND"),
    ("MSM", SUPPORTED, "INGREDIENT_FOUND"),
    ("유산균", SUPPORTED, "INGREDIENT_ALIAS"),
    ("홍삼", SUPPORTED, "INGREDIENT_PART"),
    ("칼슘", SUPPORTED, "INGREDIENT_PART"),
    ("6년근 홍삼농축액", UNCLEAR, "BRAND_OR_MODIFIER"),
    ("LACTO-5X™", UNCLEAR, "BRAND_OR_MODIFIER"),
    ("CJLP133", UNCLEAR, "BRAND_OR_MODIFIER"),
    ("멀티비타민", UNCLEAR, "CATEGORY_TERM"),
    ("미네랄", UNCLEAR, "CATEGORY_TERM"),
    ("비타민", UNCLEAR, "CATEGORY_TERM"),
    ("비타민B군", UNCLEAR, "CATEGORY_TERM"),
    ("비타민 3종", UNCLEAR, "CATEGORY_TERM"),
    ("아연", VIOLATION, "INGREDIENT_ABSENT"),
    ("셀렌", VIOLATION, "INGREDIENT_ABSENT"),
    ("콜라겐", VIOLATION, "INGREDIENT_ABSENT"),
    ("히알루론산", VIOLATION, "INGREDIENT_ABSENT"),
    ("단백질", UNCLEAR, "CONSTITUENT_POSSIBLE"),
    ("합성향료", UNCLEAR, "INGREDIENT_UNMATCHED"),
    ("영양소", UNCLEAR, "CATEGORY_TERM"),
    ("대두", UNCLEAR, "INGREDIENT_UNMATCHED"),
])
def test_each_ingredient(name, status, code):
    assert codes(run(name, [name])) == [(status, code)]


def test_b1_is_not_found_in_b12():
    assert codes(run("비타민B1", ["비타민B1"])) == [(VIOLATION, "INGREDIENT_ABSENT")]


def test_alias_in_own_dictionary_is_used_when_specific():
    prod = product(RAWMTRL_DICT_INFO=[{"RPRSNT_RAWMTRL_NM": "마리골드", "ENG_NM": "Lutein", "SCNM": "", "RAWMTRL_NCKNM": ""}])
    assert codes(run("Lutein", ["Lutein"], prod)) == [(SUPPORTED, "INGREDIENT_ALIAS")]


def test_alias_shared_by_two_ingredients_is_not_used():
    prod = product(RAWMTRL_DICT_INFO=[{"RPRSNT_RAWMTRL_NM": "가", "ENG_NM": "", "SCNM": "", "RAWMTRL_NCKNM": "대두"}])
    assert codes(run("대두", ["대두"], prod)) == [(UNCLEAR, "INGREDIENT_UNMATCHED")]


def test_common_omega3_name():
    prod = product(RAWMTRL_NM="EPA 및 DHA 함유 유지")
    assert codes(run("오메가-3", ["오메가-3"], prod)) == [(SUPPORTED, "INGREDIENT_ALIAS")]
    assert codes(run("rTG 오메가-3", ["rTG 오메가-3"], prod)) == [(UNCLEAR, "BRAND_OR_MODIFIER")]
    assert codes(run("EPA", ["EPA"], prod)) == [(SUPPORTED, "INGREDIENT_PART")]


@pytest.mark.parametrize("text,name", [("우유, 대두 함유", "우유"), ("알레르기 정보 : 대두·쇠고기 함유", "쇠고기")])
def test_allergen_notice_is_unclear(text, name):
    assert codes(run(text, [name])) == [(UNCLEAR, "ALLERGEN_NOTICE")]


def test_alias_only_name_is_not_violation():
    assert codes(run("우유로 만든", ["우유"]))[0][0] == UNCLEAR


@pytest.mark.parametrize("name,status,code", [
    ("연질캡슐", SUPPORTED, "FORM_MATCHES"),
    ("장용성", UNCLEAR, "FORM_NOT_CONFIRMED"),
])
def test_form(name, status, code):
    assert codes(run(name, [name])) == [(status, code)]


def test_empty_ingredients():
    assert codes(run("포도맛", [])) == [(UNCLEAR, "NO_INGREDIENT_SLOT")]


def test_each_ingredient_has_its_own_check():
    checks = run("비타민C + 아연", ["비타민C", "아연"])
    assert codes(checks) == [(SUPPORTED, "INGREDIENT_FOUND"), (VIOLATION, "INGREDIENT_ABSENT")]
    assert checks[1].evidence and checks[0].evidence[0]["field"] == "RAWMTRL_NM"


def test_nutrient_alias_inside_mixture_name():
    prod = product(ETC_RAWMTRL_NM="정제수, 비오틴 혼합분말")
    assert codes(run("비오틴", ["비오틴"], prod)) == [(SUPPORTED, "INGREDIENT_PART")]


def test_short_nutrient_alias_does_not_match_inside_word():
    prod = product(ETC_RAWMTRL_NM="인삼농축액, 어성초")
    assert codes(run("인", ["인"], prod))[0][1] != "INGREDIENT_PART"
    assert part_names("마그네슘") == {"마그네슘", "magnesium"}


def test_modifier_with_general_name_in_parentheses_is_not_supported():
    prod = product(RAWMTRL_NM="EPA 및 DHA 함유 유지")
    assert codes(run("x", ["rTG오메가3(EPA 및 DHA 함유 유지)"], prod)) == [(UNCLEAR, "BRAND_OR_MODIFIER")]
    assert codes(run("x", ["루테인(비타민 C)"], prod)) == [(SUPPORTED, "INGREDIENT_FOUND")]


def test_fermentation_microbe_is_not_contained_ingredient():
    prod = product(RAWMTRL_NM="유산균발효굴추출물(FGO)", INDIV_RAWMTRL_NM="", ETC_RAWMTRL_NM="", BASE_STANDARD="")
    assert codes(run("바다의 우유,굴 × 유산균 발효", ["유산균"], prod)) == [(UNCLEAR, "INGREDIENT_UNMATCHED")]
    assert codes(run("바다의 우유,굴 × 유산균 발효", ["굴"], prod)) == [(SUPPORTED, "INGREDIENT_ALIAS")]


@pytest.mark.parametrize("name,field", [("Lutein", "루테인지아잔틴복합추출물"), ("Zeaxanthin", "루테인지아잔틴복합추출물"),
                                        ("돼지감자 추출분말", "뚱딴지추출분말"), ("피쉬콜라겐", "생선콜라겐")])
def test_common_names(name, field):
    prod = product(ETC_RAWMTRL_NM=field)
    assert run(name, [name], prod)[0].status == (UNCLEAR if name == "돼지감자 추출분말" else SUPPORTED)


def test_vitamin_letter_after_vitamin_is_restored():
    prod = product(RAWMTRL_NM="비타민 D, 비타민 E")
    assert [c.status for c in run("비타민D, E", ["비타민D", "E"], prod)] == [SUPPORTED, SUPPORTED]
    assert codes(run("E", ["E"], prod)) == [(UNCLEAR, "INGREDIENT_UNMATCHED")]


def test_latin_name_in_own_dictionary_is_trusted_even_if_shared():
    prod = product(RAWMTRL_DICT_INFO=[{"RPRSNT_RAWMTRL_NM": "L. plantarum", "ENG_NM": "", "SCNM": "",
                                       "RAWMTRL_NCKNM": "Lactobacillus plantarum"}])
    assert codes(run("x", ["Lactobacillus plantarum"], prod)) == [(SUPPORTED, "INGREDIENT_ALIAS")]


@pytest.mark.parametrize("name,code", [("Vitamins", "CATEGORY_TERM"), ("AlaskOmega", "BRAND_OR_MODIFIER")])
def test_english_category_and_brand(name, code):
    assert codes(run(name, [name])) == [(UNCLEAR, code)]


@pytest.mark.parametrize("text", ["유럽산 콜라겐으로 만든 영국산 비타민C", "자연수확한 유럽산 콜라겐 사용"])
def test_raw_source_is_not_absent_ingredient(text):
    assert codes(run(text, ["콜라겐"])) == [(UNCLEAR, "RAW_SOURCE")]


def test_named_mixture_additive_does_not_hide_vitamin():
    prod = product(ETC_RAWMTRL_NM="청포도향, 혼합제제, 글루콘산아연")
    assert codes(run("부원료 비타민B1", ["비타민B1"], prod)) == [(VIOLATION, "INGREDIENT_ABSENT")]


def test_mixture_hides_non_nutrient_but_not_vitamin():
    prod = product(INDIV_RAWMTRL_NM="유산균혼합분말")
    assert codes(run("콜라겐", ["콜라겐"], prod)) == [(UNCLEAR, "CONSTITUENT_POSSIBLE")]
    assert codes(run("아연", ["아연"], prod)) == [(VIOLATION, "INGREDIENT_ABSENT")]
