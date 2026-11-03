import pytest

from claim_verification.claim_types.checkers.quantity import check_quantity
from claim_verification.finding import SUPPORTED, UNCLEAR, VIOLATION

OUT_OF_SCOPE = "OUT_OF_SCOPE"
SPEC = ("1) 성상 : 분말\n2) 아연 : 표시량(8.5 mg/500 mg)의 80~150%\n3) 비타민B12 : 표시량(2.4μg/500mg)의 80~180%\n"
        "4) 비타민B1 : 표시량(1.2mg/500mg)의 80~180%\n5) 비타민A : 표시량(700 μg RE/500mg)의 80~150%\n"
        "6) EPA와 DHA의 합 : 표시량(600 mg/1000 mg)의 80~120%\n7) 엠에스엠(MSM) : 표시량(300 mg/500 mg)의 80~120%")


def product(spec=SPEC, srv="1일 2회, 1회 1정(500mg)을 물과 함께 섭취하십시오.", name="제품", **db):
    quantity = {"BASE_STANDARD": spec, "SRV_USE": srv, "DISTB_PD": "제조일로부터 24개월", "BSSH_PRMS_DT": "20000101",
                "RAWMTRL_STD_INFO": []}
    quantity.update(db)
    return {"product_name": name, "match": {"matched_name": name, "matched_company": "(주)서흥"},
            "DB": {"QUANTITY": quantity}}


def run(text, ingredients=(), basis=None, prod=None):
    claim = {"text": text, "ingredients": list(ingredients), "intake_basis": basis}
    return check_quantity(claim, prod or product())


def codes(checks):
    return [(c.status, c.code) for c in checks]


@pytest.mark.parametrize("text,ingredients,basis,status,code", [
    ("11% 할인가 37,730원", (), None, OUT_OF_SCOPE, "SALES_OR_RANK"),
    ("대한민국 1등 오메가3", (), None, OUT_OF_SCOPE, "SALES_OR_RANK"),
    ("데이팩 1천만 포 판매달성", (), None, OUT_OF_SCOPE, "SALES_OR_RANK"),
    ("시험 방법 : 유산균발효굴추출물(FGO) 500mg/day", ("유산균발효굴추출물(FGO)",), "인체적용시험", OUT_OF_SCOPE, "STUDY_CONDITION"),
    ("L. rhamnosus CBT-LR5 221배 증가", (), None, OUT_OF_SCOPE, "STUDY_CONDITION"),
    ("혈당수치 20% 감소 확인", (), "Hard Gel 섭취군", OUT_OF_SCOPE, "STUDY_CONDITION"),
    ("380 mg x 30캡슐(11.4 g)", (), "포장 내용량", UNCLEAR, "PACKAGE_NOT_IN_EVIDENCE"),
    ("93.6 g(1,560 mg×60 정)", (), None, UNCLEAR, "PACKAGE_NOT_IN_EVIDENCE"),
    ("20 mL", (), "파우치 내용량", UNCLEAR, "PACKAGE_NOT_IN_EVIDENCE"),
    ("건강기능식품 기능성 인정 일일섭취량, 아연으로서 10~20mg/일", ("아연",), None, UNCLEAR, "REFERENCE_CLAIM"),
    ("일일섭취량, 아연으로서 10~20mg/일", ("아연",), None, UNCLEAR, "REFERENCE_RANGE"),
    ("21가지 비타민과 미네랄", ("비타민",), None, UNCLEAR, "COUNT_NOT_VERIFIED"),
    ("눈 17시간", (), None, UNCLEAR, "QUANTITY_UNCLASSIFIED"),
    ("고함량 건강한 생유산균 500억(CJLP133) 식약처 고시 최소 기준", ("프로바이오틱스",), None, UNCLEAR, "REFERENCE_CLAIM"),
    ("900mg* 최고함량 오메가3", (), None, UNCLEAR, "REFERENCE_CLAIM"),
    ("2X 비타민 B군 2배 UP*", (), "*센트룸 맨 함량 대비", UNCLEAR, "COMPARISON_NOT_VERIFIED"),
    ("보장균수 2배 증량", (), None, UNCLEAR, "COMPARISON_NOT_VERIFIED"),
    ("비코팅 유산균 섭취 그룹 20명, 듀얼코팅 유산균 섭취 그룹 20명", (), None, OUT_OF_SCOPE, "STUDY_CONDITION"),
    ("*%의 수치는 1일 영양성분기준치에 대한 비율임", (), None, OUT_OF_SCOPE, "FOOTNOTE"),
])
def test_classification(text, ingredients, basis, status, code):
    assert codes(run(text, ingredients, basis)) == [(status, code)]


def test_percent_consistent_and_label_match():
    assert codes(run("아연 8.5 mg(100 %)", ("아연",))) == [(SUPPORTED, "PERCENT_CONSISTENT"), (SUPPORTED, "AMOUNT_MATCHES_LABEL")]


def test_percent_mismatch_is_violation():
    assert codes(run("아연 8.5 mg(200 %)", ("아연",))) == [(VIOLATION, "PERCENT_MISMATCH")]


def test_percent_allows_rounding():
    assert run("지방 0.7 g(0%)", ("지방",))[0].status == SUPPORTED


def test_percent_reads_each_nutrient_in_table():
    checks = run("1일 섭취량 당 함량 : 열량 12 kcal, 탄수화물 2 g (1 %), 나트륨 10 mg 1%")
    assert [c.target for c in checks] == ["탄수화물", "나트륨"]
    assert {c.code for c in checks} == {"PERCENT_CONSISTENT"}


def test_percent_uses_exact_nutrient_not_prefix():
    checks = run("비타민B₁₂ 2.4 μg(100%)", ("비타민B₁₂",))
    assert [c.target for c in checks][0] == "비타민B12"
    assert all(c.status == SUPPORTED for c in checks)


def test_infant_product_is_unclear_even_if_percent_is_off():
    prod = product(name="락토핏 베이비")
    assert codes(run("아연 8.5 mg(200 %)", ("아연",), prod=prod)) == [(UNCLEAR, "INFANT_PRODUCT")]


def test_rae_cannot_use_annex_re():
    assert codes(run("비타민A 700 μg RAE(100%)", ("비타민A",))) == [(UNCLEAR, "BASIS_MISMATCH")]


def test_unknown_nutrient_percent_is_unclear():
    assert codes(run("루테인 20 mg(100%)", ("루테인",))) == [(UNCLEAR, "BASIS_MISMATCH")]


def test_label_percent_match_and_unknown_basis():
    assert codes(run("아연 100%", ("아연",))) == [(SUPPORTED, "PERCENT_MATCHES_LABEL")]
    assert codes(run("아연 200%", ("아연",))) == [(UNCLEAR, "PERCENT_NOT_CONFIRMED")]


def test_percent_without_nutrient_is_not_a_percent_check():
    assert run("100% 식물성", ())[0].code == "QUANTITY_UNCLASSIFIED"


def test_amount_matches_label():
    assert codes(run("아연 8.5mg", ("아연",))) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]


def test_amount_matches_daily():
    assert codes(run("아연 17mg", ("아연",))) == [(SUPPORTED, "AMOUNT_MATCHES_DAILY")]


def test_amount_differs_from_label_and_daily_is_violation():
    checks = run("아연 12mg", ("아연",))
    assert codes(checks) == [(VIOLATION, "AMOUNT_MISMATCH")]
    assert checks[0].evidence[0]["field"] == "BASE_STANDARD"


def test_amount_without_daily_product_uses_serving_factors():
    prod = product(srv="1일 1회, 1회 2정을 물과 함께")
    assert codes(run("아연 12mg", ("아연",), prod=prod)) == [(VIOLATION, "AMOUNT_MISMATCH")]
    assert codes(run("아연 17mg", ("아연",), prod=prod)) == [(SUPPORTED, "AMOUNT_MATCHES_SERVING")]
    assert codes(run("아연 4.25mg", ("아연",), prod=prod)) == [(SUPPORTED, "AMOUNT_MATCHES_SERVING")]


def test_amount_concentration_or_unknown_intake_is_unclear():
    concentration = product(spec="2) 아연 : 표시량(5 mg/1 g)", srv="1일 1회, 1회 1포")
    assert codes(run("아연 12mg", ("아연",), prod=concentration)) == [(UNCLEAR, "BASIS_MISMATCH")]
    no_intake = product(srv="건강기능식품 원료로 사용")
    assert codes(run("아연 12mg", ("아연",), prod=no_intake)) == [(UNCLEAR, "BASIS_MISMATCH")]


def test_vitamin_d_iu_is_converted():
    prod = product(spec="2) 비타민D : 표시량(100μg/1.04g)")
    assert codes(run("비타민D 4,000 IU", ("비타민D",), prod=prod)) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]


def test_other_iu_is_not_converted():
    prod = product(spec="2) 비타민E : 표시량(11mg α-TE/1g)")
    assert codes(run("비타민E 16 IU", ("비타민E",), prod=prod)) == [(UNCLEAR, "BASIS_MISMATCH")]


@pytest.mark.parametrize("text,basis", [("영국산 100%", None), ("일일 섭취량 대비 100% 충족", None)])
def test_percent_without_reference_is_not_nutrient_percent(text, basis):
    assert run(text, ("아연",), basis)[0].code == "QUANTITY_UNCLASSIFIED"


def test_single_ingredient_percent_needs_reference_word():
    checks = run("비타민 B1 식약처 일일 영양성분기준치 대비 100% 충족", ("비타민 B1",))
    assert checks[0].code == "PERCENT_MATCHES_LABEL"


def test_b12_is_not_compared_with_b1():
    assert codes(run("비타민B1 1.2mg", ("비타민B1",))) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]
    prod = product(spec="2) 비타민B1 : 표시량(1.2mg/500mg)의 80~180%")
    assert codes(run("비타민B12 2.4 μg", ("비타민B12",), prod=prod)) == [(UNCLEAR, "SPEC_NOT_FOUND")]


@pytest.mark.parametrize("text,ingredients", [
    ("EPA+DHA 600 mg", ()),
    ("EPA와 DHA의 합 600 mg", ("EPA", "DHA")),
    ("1일 섭취량 당 MSM 300 mg", ("MSM",)),
])
def test_alternative_names_find_spec(text, ingredients):
    assert codes(run(text, ingredients)) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]


def test_oil_weight_is_not_compared_with_sum():
    assert codes(run("EPA 및 DHA 함유 유지 1000 mg", ("EPA 및 DHA 함유 유지",))) == [(UNCLEAR, "SPEC_NOT_FOUND")]


def test_mention_keeps_nutrient_digit_boundary():
    prod = product(spec="2) 비타민B1 : 표시량(1.2mg/500mg)의 80~180%")
    assert codes(run("비타민B1 1.2mg", (), prod=prod)) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]
    assert run("비타민B12 2.4 μg", (), prod=prod)[0].code == "QUANTITY_UNCLASSIFIED"


def test_several_values_are_not_guessed():
    assert codes(run("아연 8.5mg, 비타민B1 1.2mg", ("아연", "비타민B1"))) == [(UNCLEAR, "MULTIPLE_VALUES")]


def test_microbe_count_without_unit_and_name():
    prod = product(spec="2) 프로바이오틱스 수 : 표시량(100억 CFU/2g) 이상")
    assert codes(run("프로바이오틱스 수 100억 CFU", ("프로바이오틱스",), prod=prod)) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]
    assert codes(run("장건강 | 100억 CFU", (), prod=prod)) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]
    assert codes(run("1일 섭취량당 프로바이오틱스 수 100억 함유", ("프로바이오틱스",), prod=prod)) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]
    assert codes(run("프로바이오틱스 수 4,000,000,000(40억) CFU", ("프로바이오틱스",), prod=prod)) == [(UNCLEAR, "BASIS_MISMATCH")]


def test_iu_is_not_compared_with_mass():
    assert codes(run("아연 4,000 IU", ("아연",))) == [(UNCLEAR, "BASIS_MISMATCH")]


@pytest.mark.parametrize("text,srv,status,code", [
    ("하루 한 포", "1일 1회, 1회 1포씩", SUPPORTED, "INTAKE_MATCHES"),
    ("1일 1포", "1일 1회, 1회 1포씩", SUPPORTED, "INTAKE_MATCHES"),
    ("하루 2정 한번에!", "1일 1회, 1회 2정", SUPPORTED, "INTAKE_MATCHES"),
    ("1일 섭취량: 1포(4.4 g)", "1일 1회, 1회 1포(4.4 g)", SUPPORTED, "INTAKE_MATCHES"),
    ("하루 한 번으로 채우는 에너지", "1일 1회, 1회 2정", SUPPORTED, "INTAKE_MATCHES"),
    ("눈건강엔 하루 한 알", "1일 1회, 1회 1캡슐", SUPPORTED, "INTAKE_MATCHES"),
    ("본 제품 1일 섭취 권장량은 1병입니다", "1일 1회, 1회 1병", SUPPORTED, "INTAKE_MATCHES"),
    ("하루 한 포", "1일 2회, 1회 1포", VIOLATION, "INTAKE_MISMATCH"),
    ("하루 한 번으로 끝", "1일 2회, 1회 1정", VIOLATION, "INTAKE_MISMATCH"),
    ("하루 한 포", "1일 1회, 1회 2캡슐", UNCLEAR, "INTAKE_UNIT_DIFFERS"),
    ("하루 한 포", "건강기능식품 원료로 사용", UNCLEAR, "INTAKE_NOT_FOUND"),
])
def test_intake(text, srv, status, code):
    assert codes(run(text, prod=product(srv=srv))) == [(status, code)]


@pytest.mark.parametrize("text,status,code", [
    ("소비기한 제조일로부터 24개월", SUPPORTED, "SHELF_LIFE_MATCHES"),
    ("소비기한 2년", SUPPORTED, "SHELF_LIFE_MATCHES"),
    ("소비기한 제조일로부터 12개월", VIOLATION, "SHELF_LIFE_MISMATCH"),
    ("소비기한 2027.04.29까지", UNCLEAR, "SHELF_LIFE_NOT_COMPARABLE"),
    ("또한 2027년까지 소비기한이 보장돼 부모님께 안심을 드립니다.", UNCLEAR, "SHELF_LIFE_NOT_COMPARABLE"),
])
def test_shelf_life(text, status, code):
    assert codes(run(text)) == [(status, code)]


def test_heritage_only_for_named_manufacturer():
    assert codes(run("120년 전통 DSM 비타민 원료 사용", ("비타민",)))[0] == (OUT_OF_SCOPE, "HERITAGE_NOT_MANUFACTURER")
    assert codes(run("서흥 76년 전통"))[0] == (UNCLEAR, "HERITAGE_NOT_CONFIRMED")


def test_cfu_with_serving_is_not_package():
    prod = product(spec="2) 프로바이오틱스 수 : 10,000,000,000(100억)CFU/5g 이상", srv="1일 1회, 1회 2포")
    assert codes(run("100억 CFU / 2포(5 g)", ("프로바이오틱스",), "2포(5 g)", prod)) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]


def test_alias_from_products_own_std_info():
    prod = product(spec="2) 엠에스엠 : 표시량(1.5g / 120ml)", srv="1일 2회, 1회 60ml",
                   RAWMTRL_STD_INFO=[{"RAWMTRL_NM": "엠에스엠(MSM, Methyl sulfonylmethane, 디메틸설폰)"}])
    assert codes(run("1일 섭취량 당 MSM 1,500 mg", ("MSM",), prod=prod)) == [(SUPPORTED, "AMOUNT_MATCHES_LABEL")]


def test_grouped_percent_checks_each_nutrient():
    spec = ("2) 판토텐산 : 표시량(25mg/1g)\n3) 비타민C : 표시량(100mg/1g)\n4) 비타민D : 표시량(10μg/1g)\n"
            "5) 비타민E : 표시량(11mg α-TE/1g)\n6) 비타민K : 표시량(70μg/1g)")
    checks = run("판토텐산 500%, 비타민C, D, E, K 100%", (), "1일 영양성분 기준치 대비", product(spec=spec))
    assert [c.target for c in checks] == ["판토텐산", "비타민C", "비타민D", "비타민E", "비타민K"]
    assert {c.code for c in checks} == {"PERCENT_MATCHES_LABEL"}


def test_bare_vitamin_b_name_in_percent_list():
    spec = "2) 비타민B1 : 표시량(3mg/1g)\n3) 판토텐산 : 표시량(14mg/1g)"
    checks = run("*1일 영양성분 기준치에 대한 비율(B1: 250%, 판토텐산: 280%)", (), None, product(spec=spec))
    assert {c.status for c in checks} == {SUPPORTED}


def test_grouped_percent_keeps_unknown_name_unclear():
    checks = run("아연 100%, 미네랄 6종 100%", ("아연", "미네랄"))
    assert codes(checks) == [(SUPPORTED, "PERCENT_MATCHES_LABEL"), (UNCLEAR, "NUTRIENT_UNRESOLVED")]


def test_heritage_matching_license_year_is_still_unclear():
    prod = product(BSSH_PRMS_DT="19500101")
    assert codes(run("서흥 76년 전통", prod=prod))[0] == (UNCLEAR, "HERITAGE_NOT_CONFIRMED")
