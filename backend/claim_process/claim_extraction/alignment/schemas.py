from dataclasses import dataclass


@dataclass
class Product:
    product_ref: str               # "p01", ...
    product_name: str | None
    brand_name: str | None
    manufacturer_name: str | None
    manufacturing_report_number: str | None


@dataclass
class FinalClaim:
    claim_id: str                  # "c01", ... 시간순
    product_ref: str | None
    text: str                      # 그룹 최상위 멤버(audio > text > scene)의 원문
    claim_type: list[str]
    ingredients: list[str]
    effect: str | None
    quantity: str | None
    intake_basis: str | None
    t_start: float
    t_end: float
