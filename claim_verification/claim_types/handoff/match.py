"""광고 제품을 data.csv 행과 연결한다.

    신고번호가 data.csv에 있으면 confirmed.
    없으면 제품명이 같은 행 중 제조사까지 일치하는 행이 하나일 때 confirmed.
    제품명 후보는 있는데 하나로 정해지지 않으면 unresolved, 후보가 없으면 not_found.

제조사가 없으면 제품명이 하나뿐이어도 confirmed로 보지 않는다. 같은 이름의 다른 제품일 수 있다.
"""

from collections import defaultdict

from ...inputs import CONFIRMED, NOT_FOUND, UNRESOLVED
from ..parsing.names import normalize_company, normalize_name

__all__ = ["BY_NAME_AND_COMPANY", "BY_REPORT_NUMBER", "ProductIndex", "normalize_company", "normalize_name"]

BY_REPORT_NUMBER = "report_number"
BY_NAME_AND_COMPANY = "name_and_company"


def _same_company(a: str, b: str) -> bool:
    return bool(a) and bool(b) and (a in b or b in a)


class ProductIndex:
    def __init__(self, rows: list[dict]):
        self.by_report_number = {r["STTEMNT_NO"]: r for r in rows}
        self.by_name = defaultdict(list)
        for r in rows:
            self.by_name[normalize_name(r["PRDUCT"])].append(r)

    def match(self, product: dict) -> tuple[str, str | None, dict | None, int]:
        """(status, method, 연결된 행, 제품명 후보 수)."""
        row = self.by_report_number.get(product.get("manufacturing_report_number"))
        if row is not None:
            return CONFIRMED, BY_REPORT_NUMBER, row, 1
        name = normalize_name(product.get("product_name"))
        candidates = self.by_name.get(name, []) if name else []
        if not candidates:
            return NOT_FOUND, None, None, 0
        company = normalize_company(product.get("manufacturer_name"))
        same = [r for r in candidates if _same_company(company, normalize_company(r["ENTRPS"]))]
        if len(same) == 1:
            return CONFIRMED, BY_NAME_AND_COMPANY, same[0], len(candidates)
        return UNRESOLVED, None, None, len(candidates)
