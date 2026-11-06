from claim_verification.claim_types.handoff.build import build_product, build_video
from claim_verification.claim_types.handoff.fields import DB_FIELDS, product_db
from claim_verification.claim_types.handoff.match import ProductIndex


def _row(name="제품 A", company="(주)서흥", number="1", **kw):
    row = {f: "" for fields in DB_FIELDS.values() for f in fields}
    row.update(PRDUCT=name, ENTRPS=company, STTEMNT_NO=number, **kw)
    return row


def _product(name="제품A", company="서흥", number=None):
    return {"product_ref": "p01", "product_name": name, "manufacturer_name": company,
            "manufacturing_report_number": number}


def test_report_number_wins_over_name():
    index = ProductIndex([_row("다른 이름", number="9")])
    status, method, row, _ = index.match(_product(company=None, number="9"))
    assert (status, method, row["STTEMNT_NO"]) == ("confirmed", "report_number", "9")


def test_name_and_company_unique_is_confirmed():
    index = ProductIndex([_row(number="1"), _row(company="종근당건강(주)", number="2")])
    status, method, row, candidates = index.match(_product())
    assert (status, method, row["STTEMNT_NO"], candidates) == ("confirmed", "name_and_company", "1", 2)


def test_name_without_company_is_unresolved():
    status, _, row, candidates = ProductIndex([_row()]).match(_product(company=None))
    assert (status, row, candidates) == ("unresolved", None, 1)


def test_company_matching_two_rows_is_unresolved():
    index = ProductIndex([_row(number="1"), _row(company="(주)서흥헬스케어", number="2")])
    assert index.match(_product())[0] == "unresolved"


def test_unknown_name_is_not_found():
    assert ProductIndex([_row()]).match(_product(name="없는 제품"))[0] == "not_found"


def test_missing_name_is_not_found():
    assert ProductIndex([_row(name="")]).match(_product(name=None))[0] == "not_found"


def test_product_db_splits_by_type_and_parses_json():
    db = product_db(_row(BASE_STANDARD="규격", RAWMTRL_STD_INFO='[{"RAWMTRL_NM": "아연"}]'))
    assert set(db) == set(DB_FIELDS)
    assert db["QUANTITY"]["BASE_STANDARD"] == "규격"
    assert db["EFFECT"]["RAWMTRL_STD_INFO"] == [{"RAWMTRL_NM": "아연"}]
    assert db["COMPOSITION"]["RAWMTRL_DICT_INFO"] == []


def test_confirmed_product_gets_db_and_report_number():
    out = build_product(_product(), ProductIndex([_row(number="1")]))
    assert out["manufacturing_report_number"] == "1"
    assert out["match"]["matched_company"] == "(주)서흥"
    assert out["DB"]["CERTIFICATION"]["STTEMNT_NO"] == "1"


def test_unmatched_product_has_no_db():
    out = build_product(_product(company=None), ProductIndex([_row()]))
    assert out["DB"] is None
    assert out["match"]["status"] == "unresolved"


def test_video_keeps_claims_as_they_are():
    claims = [{"claim_id": "c01", "text": "t"}]
    video = {"video_id": "v1", "url": "u", "products": [_product()], "claims": claims}
    out = build_video(video, ProductIndex([_row()]), "v")
    assert out["claims"] == claims
    assert out["db_version"] == "v"
