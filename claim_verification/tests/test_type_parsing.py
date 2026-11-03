import re
from pathlib import Path

import pytest

from claim_verification.claim_types.parsing.intake import parse_intake
from claim_verification.claim_types.parsing.lexicon import Lexicon, ingredient_key, split_ingredients, strip_note
from claim_verification.claim_types.parsing.nutrients import DAILY_VALUES, canonical, daily_value
from claim_verification.claim_types.parsing.spec import daily_amount, parse_spec
from claim_verification.claim_types.parsing.units import Amount, comparable, parse_amounts, same_amount
from claim_verification.scripts.build_ingredient_lexicon import build_terms

ANNEX = Path(__file__).resolve().parents[2] / "data" / "enrichment" / "1일_영양성분_기준치.md"


@pytest.mark.parametrize("text,expected", [
    ("1,840mg", [Amount(1840, "mg")]),
    ("비타민B₁₂ 2.4 ㎍", [Amount(2.4, "μg")]),
    ("100억 CFU", [Amount(1e10, "CFU")]),
    ("5억 마리", [Amount(5e8, "CFU")]),
    ("5 x 10⁸ CFU", [Amount(5e8, "CFU")]),
    ("11 mg α-TE", [Amount(11, "mg", "α-TE")]),
    ("15 mgNE", [Amount(15, "mg", "NE")]),
    ("700 μg RAE", [Amount(700, "μg", "RAE")]),
    ("10 kcal", [Amount(10, "kcal")]),
    ("700 μgRE", [Amount(700, "μg", "RE")]),
    ("11 mg a-TE", [Amount(11, "mg", "α-TE")]),
    ("3가지 60정 11%", []),
    ("OMEGA3 5gold", []),
    ("10⁸ CFU", []),
    ("1e8 CFU", []),
    ("1×10^-3 g", []),
    ("5.0.E+09 CFU/2 g", [Amount(2, "g")]),
    ("50, 100, 200 mg/kg", []),
    ("칼슘 300mg, 500mg", [Amount(300, "mg"), Amount(500, "mg")]),
    ("비타민E500mg", [Amount(500, "mg")]),
])
def test_parse_amounts(text, expected):
    assert parse_amounts(text) == expected


def test_comparable_and_same():
    assert same_amount(Amount(1, "g"), Amount(1000, "mg"))
    assert not same_amount(Amount(500, "mg"), Amount(600, "mg"))
    assert not comparable(Amount(1, "g"), Amount(1, "mL"))
    assert not comparable(Amount(700, "μg", "RAE"), Amount(700, "μg", "RE"))
    assert comparable(Amount(700, "μg"), Amount(700, "μg", "RE"))
    assert same_amount(Amount(0, "mg"), Amount(0, "g"))


@pytest.mark.parametrize("name,expected", [
    ("비타민B₁₂", "비타민B12"), ("비타민 B1", "비타민B1"), ("VITAMIN B₁", "비타민B1"), ("vit B2", "비타민B2"),
    ("철", "철분"), ("Iron", "철분"), ("비오틴", "바이오틴"), ("셀렌", "셀레늄"), ("Mg", "마그네슘"),
    ("루테인", None), ("비타민", None), ("철분 키즈", None),
])
def test_nutrient_names_match_whole_name_only(name, expected):
    assert canonical(name) == expected


def test_daily_value():
    assert daily_value("철") == Amount(12, "mg")
    assert daily_value("루테인") is None


@pytest.mark.skipif(not ANNEX.exists(), reason="별표 5 원문 없음")
def test_daily_values_match_annex():
    found = {}
    for line in ANNEX.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not line.startswith("|") or "---" in line or "영양성분(단위)" in line:
            continue
        for name, value in zip(cells[::2], cells[1::2]):
            found[re.match(r"(.+?)\(", name)[1]] = float(value.replace(",", ""))
    assert {k: v.value for k, v in DAILY_VALUES.items()} == found


@pytest.mark.parametrize("line,name,amount,per", [
    ("2) 루테인 : 표시량(18.2 mg/0.5g)의 80~120%", "루테인", Amount(18.2, "mg"), Amount(0.5, "g")),
    ("4. 비타민B1 : 표시량[1.2mg/1000mg]의 80~180%", "비타민B1", Amount(1.2, "mg"), Amount(1000, "mg")),
    ("3-2) EPA와 DHA의 합 : 표시량{600 mg / 2,240 mg}의 80 ~ 120%", "EPA와 DHA의 합", Amount(600, "mg"), Amount(2240, "mg")),
    ("6) 비타민E : 표시량(11 mg α-TE/0.5g)의 80~150%", "비타민E", Amount(11, "mg", "α-TE"), Amount(0.5, "g")),
    ("(6) 나이아신 : 표시량(15 mgNE/900 mg)의 80% 이상 150% 이하", "나이아신", Amount(15, "mg", "NE"), Amount(900, "mg")),
    ("4. 비타민D: 표시량(5μg(200IU)/2g)의 80~180%", "비타민D", Amount(5, "μg"), Amount(2, "g")),
    ("2 구리 : 표시량의 80 ~ 150% (표시량 : 0.465 mg / 2,650 mg)", "구리", Amount(0.465, "mg"), Amount(2650, "mg")),
    ("② 진세노사이드 Rg1, Rb1 및 Rg3의 합 :최종제품 - 표시량(3.840㎎/9.6g)의 80% 이상", "진세노사이드 Rg1, Rb1 및 Rg3의 합",
     Amount(3.84, "mg"), Amount(9.6, "g")),
    ("2) 콘드로이친 황산나트륨 : 표시량(1080 /3575mg)의 80~120%", "콘드로이친 황산나트륨", Amount(1080, "mg"), Amount(3575, "mg")),
    ("2) 프로바이오틱스 수 : 표시량(400,000,000,000(4,000억) CFU/g) 이상", "프로바이오틱스", Amount(4e11, "CFU"), Amount(1, "g")),
    ("2. 프로바이오틱스 수(표시량 300,000,000,000(3,000억) CFU/g) : 표시량 이상", "프로바이오틱스", Amount(3e11, "CFU"), Amount(1, "g")),
    ("2. 프로바이오틱스 수 : 3,000,000,000(30억) CFU/2g 이상", "프로바이오틱스", Amount(3e9, "CFU"), Amount(2, "g")),
    ("2 프로바이오틱스 수: 표시량(4,000억 CFU/g) 이상", "프로바이오틱스", Amount(4e11, "CFU"), Amount(1, "g")),
    ("3. 프로바이오틱스 수 : 표시량(1억cfu / 4 g) 이상", "프로바이오틱스", Amount(1e8, "CFU"), Amount(4, "g")),
    ("4 아연(mg/450 mg) : 표시량(2.55)의 80~150%", "아연", Amount(2.55, "mg"), Amount(450, "mg")),
    ("8나이아신 : 표시량(15 mgNE /2,500 mg)의 80~150%", "나이아신", Amount(15, "mg", "NE"), Amount(2500, "mg")),
    ("10나이아신 : 5mgNE /1,400mg 표시량의 80~150%", "나이아신", Amount(5, "mg", "NE"), Amount(1400, "mg")),
    ("5. 6,7-Dimethylesculetin - 표시량[0.069 mg/1정(800mg)]의 80~120%", "6,7-Dimethylesculetin", Amount(0.069, "mg"), Amount(800, "mg")),
    ("2) 헤스페리딘 함량(mg/g) : 표시량(0.68 mg/3,500 mg)의 80 ~ 120%", "헤스페리딘", Amount(0.68, "mg"), Amount(3500, "mg")),
    ("12) 비타민D : 표시량의 80~180% (7.8 ㎍/3, 000 mg)", "비타민D", Amount(7.8, "μg"), Amount(3000, "mg")),
    ("3 비타민B1(mg) : 표시량(0.59mg/30g)의 80~180%", "비타민B1", Amount(0.59, "mg"), Amount(30, "g")),
    ("2 비타민C 함량 : 표시량(100mg/1g)의 80~150%", "비타민C", Amount(100, "mg"), Amount(1, "g")),
    ("2EPA와 DHA의 합 : 표시량(600mg/1g)의 80~120%", "EPA와 DHA의 합", Amount(600, "mg"), Amount(1, "g")),
    ("2)프로바이오틱스균수 : 표시량(1억/1.5g) 이상", "프로바이오틱스균", Amount(1e8, "CFU"), Amount(1.5, "g")),
    ("2 비타민E(mg α-TE) : 표시량(11mg α-TE/1g)의 80~150%", "비타민E", Amount(11, "mg", "α-TE"), Amount(1, "g")),
    ("2 비타민B2으로서 : 표시량(1.4mg/1g)의 80~150%", "비타민B2", Amount(1.4, "mg"), Amount(1, "g")),
    ("3 프로바이오틱스 수 : 2.7 X 10^11 CFU/g (2,700억) 이상", "프로바이오틱스", Amount(2.7e11, "CFU"), Amount(1, "g")),
])
def test_parse_spec_line(line, name, amount, per):
    items = parse_spec(line)
    assert len(items) == 1
    assert (items[0].name, items[0].amount, items[0].per) == (name, amount, per)


@pytest.mark.parametrize("line", [
    "1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 분말",
    "4. 납 : 1.0 mg/kg 이하",
    "3) 납(mg/kg) : 0.5 이하",
    "7) 대장균군 : 음성",
    "2. 일반 세균수 : 1mL 당 3,000이하",
    "3. 세균수 : 3,000 CFU/g 이하",
    "세균수 : 3,000 cfu/g",
    "2) 옥타코사놀 : 표시량(40 mg / 1.000 mg)의 80 ~ 120 %",
    "2) 엠에스엠(MSM) : 표시량(1,500mg/4.400mg)의 80~120%",
    "4. 마그네슘(mg/1.400mg) : 표시량(97)의 80~150%.",
    "2) 루테인 : 표시량(1억/2g)의 80~120%",
    "2) 칼슘 : 표시량(500 mg/100 mg)의 80~150%",
    "2) Akkermansia muciniphila EB-AMDK19 사균체수(cells/g): 2.0E+11/g(표시량의 70~130%)",
    "2. 프로바이오틱스 수 : 표시량(5.0.E+09 CFU/2 g) 이상",
])
def test_parse_spec_ignores_non_label_lines(line):
    assert parse_spec(line) == []


def test_parse_spec_reads_each_line():
    text = "1) 성상 : 분말\n2) 비타민B12 : 표시량(2.4μg/500mg)의 80~180%\n3) 비타민B1 : 표시량(1.2mg/500mg)의 80~180%"
    assert [i.name for i in parse_spec(text)] == ["비타민B12", "비타민B1"]


@pytest.mark.parametrize("text,times,count,unit,product", [
    ("1일 1회, 1회 1캡슐(0.5g)을 물과 함께 섭취하십시오.", 1, 1, "캡슐", Amount(0.5, "g")),
    ("1일 2회, 1회 2정을 충분한 물과 함께", 2, 2, "정", None),
    ("1일2회, 1회(5g) 1포씩 섭취", 2, 1, "포", Amount(5, "g")),
    ("1일 1회 1포", 1, 1, "포", None),
    ("1일 2캡슐을 충분한 물과 함께 섭취하십시오.", 1, 2, "캡슐", None),
    ("1일, 1회, 1회 1포(멀티팩)를 물과 함께", 1, 1, "포", None),
    ("1일 1회 1병(액상 30 mL + 정제 500 mg×2정) 섭취", 1, 1, "병", None),
    ("1일 1회, 1회 1병(30ml)을 흔들어서", 1, 1, "병", Amount(30, "ml")),
    ("1일 1회, 1회 2정(1정당 500mg)", 1, 2, "정", None),
    ("1일 1회, 1회 1포(1포 : 비타민C정제 650mg)를", 1, 1, "포", None),
])
def test_parse_intake(text, times, count, unit, product):
    i = parse_intake(text)
    assert (i.times_per_day, i.count_per_time, i.count_unit, i.product_per_time) == (times, count, unit, product)


@pytest.mark.parametrize("text", ["건강기능식품 원료로 사용", "", None])
def test_parse_intake_without_dose(text):
    assert parse_intake(text) is None


def test_daily_total_is_not_multiplied_again():
    i = parse_intake("1일 3회, 1회 12정씩 물과 함께 섭취(일일섭취량 : 36정(6.12g))")
    assert (i.times_per_day, i.count_per_time, i.product_per_time) == (3, 12, None)
    assert i.daily_product == Amount(6.12, "g")
    item = parse_spec("총 엽록소 : 표시량(110.16mg/6.12g)의 80~120%")[0]
    assert daily_amount(item, i) == Amount(110.16, "mg")


def test_spoon_capacity_is_not_product_amount():
    i = parse_intake("1일3회 1회에 동봉된 스푼(1스푼 5.5g정도)을 이용하여 2스푼(11g)을 그대로 섭취한다.")
    assert i.times_per_day == 3
    assert i.daily_product is None


def test_daily_total_after_sentence():
    i = parse_intake("1일 1회, 1회 1포씩 공복이나 식전에 섭취하십시오.(1일섭취량 : 90ml)")
    assert i.daily_product == Amount(90, "ml")


def test_intake_daily_values():
    i = parse_intake("1일 2회, 1회 1캡슐(1 g)")
    assert i.daily_count == 2
    assert i.daily_product == Amount(2, "g")


@pytest.mark.parametrize("text", [
    "1일 1회, 1회 2포(2g)를 직접 섭취",
    "1일 1회, 1회 2포(2g/포)를 직접 섭취",
    "1일 1회, 1회 1포(정제 2정, 액상 30g)를 직접 섭취.",
    "1일 1회, 1회 1포(정제 1500mg 3EA)를 씹어서 섭취하십시오",
])
def test_ambiguous_parenthesis_is_not_product_amount(text):
    assert parse_intake(text).daily_product is None


def test_gram_count_is_product_amount():
    i = parse_intake("1일 2회, 1회 0.45g(0.15g씩 약 3회 분사)를 구강에 분무하여 섭취하십시오.")
    assert i.daily_product == Amount(0.9, "g")


def test_daily_amount_scales_by_daily_product():
    item = parse_spec("비타민C : 표시량(30 mg/0.5g)의 80~150%")[0]
    assert daily_amount(item, parse_intake("1일 1회, 1회 1캡슐(0.5g)")) == Amount(30, "mg")
    assert daily_amount(item, parse_intake("1일 2회, 1회 1캡슐(0.5g)")) == Amount(60, "mg")


def test_daily_amount_unknown_without_product_weight():
    item = parse_spec("비타민C : 표시량(30 mg/0.5g)의 80~150%")[0]
    assert daily_amount(item, parse_intake("1일 1회, 1회 1캡슐")) is None
    assert daily_amount(item, None) is None
    assert daily_amount(item, parse_intake("1일 1회, 1회 1병(30ml)")) is None


def test_strip_note_and_key():
    assert strip_note("비타민 B2(고시형)") == "비타민 B2"
    assert strip_note("HK표고버섯균사체(기능성원료인정제2010-35호)") == "HK표고버섯균사체"
    assert strip_note("LACTO-5X™") == "LACTO-5X"
    assert ingredient_key("철") == ingredient_key("Iron") == "철분"
    assert ingredient_key("비타민 B1") != ingredient_key("비타민B12")


def test_split_ingredients_keeps_parentheses():
    assert split_ingredients("저당, 식물혼합농축액(대추60%,구기자12%), 비타민 C") == \
        ["저당", "식물혼합농축액(대추60%,구기자12%)", "비타민 C"]
    assert split_ingredients(None) == []


def _row(std=(), dictionary=()):
    import json
    return {"RAWMTRL_STD_INFO": json.dumps(list(std)), "RAWMTRL_DICT_INFO": json.dumps(list(dictionary))}


def _dict_entry(name, eng="", sci="", nick=""):
    return {"RPRSNT_RAWMTRL_NM": name, "ENG_NM": eng, "SCNM": sci, "RAWMTRL_NCKNM": nick}


def test_lexicon_keeps_std_names_missing_from_dict():
    lex = Lexicon(build_terms([_row(std=[{"RAWMTRL_NM": "아연"}])]))
    assert lex.is_specific("아연")
    assert lex.is_specific("zinc")


def test_lexicon_alias_shared_by_two_ingredients_is_not_specific():
    lex = Lexicon(build_terms([_row(dictionary=[_dict_entry("소연골분말", nick="우유"),
                                                _dict_entry("락토페린(제2023-38호)", nick="우유, Lf")])]))
    assert lex.lookup("우유") == ["락토페린", "소연골분말"]
    assert not lex.is_specific("우유")


def test_alias_is_not_representative():
    lex = Lexicon(build_terms([_row(dictionary=[_dict_entry("락토페린(제2023-38호)", nick="우유")])]))
    assert lex.is_specific("우유")
    assert not lex.is_representative("우유")
    assert lex.is_representative("락토페린")


def test_lexicon_drops_digit_and_single_letter_terms():
    lex = Lexicon(build_terms([_row(dictionary=[_dict_entry("펙틴", nick="1, 6, 가")])]))
    assert lex.terms == {"펙틴": ["펙틴"]}
