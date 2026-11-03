"""claim_type별로 판정에 넘길 data.csv 필드."""

import json

DB_FIELDS = {
    "QUANTITY": ("BASE_STANDARD", "SRV_USE", "DISTB_PD", "PRDT_SHAP_CD_NM", "BSSH_PRMS_DT", "INTAKE_HINT1",
                 "RAWMTRL_STD_INFO"),
    "COMPOSITION": ("RAWMTRL_NM", "INDIV_RAWMTRL_NM", "ETC_RAWMTRL_NM", "CAP_RAWMTRL_NM", "PRDLST_CDNM",
                    "BASE_STANDARD", "SUNGSANG", "RAWMTRL_DICT_INFO"),
    "CERTIFICATION": ("STTEMNT_NO", "PRMS_DT", "INDUTY_CD_NM", "MAIN_FNCTN", "RAWMTRL_NM", "INDIV_RAWMTRL_NM",
                      "RAWMTRL_STD_INFO", "RAWMTRL_CLASS_INFO"),
    "EFFECT": ("MAIN_FNCTN", "INTAKE_HINT1", "RAWMTRL_STD_INFO"),
}

# data.csv에 JSON 문자열로 들어 있는 필드. 비어 있으면 빈 목록이다.
JSON_FIELDS = {"RAWMTRL_STD_INFO", "RAWMTRL_DICT_INFO", "RAWMTRL_CLASS_INFO"}


def product_db(row: dict) -> dict:
    """data.csv 한 행 → {"QUANTITY": {...}, "COMPOSITION": {...}, ...}."""
    return {claim_type: {f: _value(row, f) for f in fields} for claim_type, fields in DB_FIELDS.items()}


def _value(row: dict, field: str):
    value = row[field]
    if field in JSON_FIELDS:
        return json.loads(value) if value else []
    return value
