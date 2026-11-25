"""SRV_USE(섭취 방법) 읽기: 1일 횟수, 1회 개수, 1회 제품량, 1일 총 제품량.

1회 제품량은 1회 개수에 바로 붙은 괄호만 읽는다("1회 1캡슐(0.5g)", "1회(5g) 1포").
다른 괄호에는 스푼 용량이나 1일 총량이 들어 있다("1스푼 5.5g정도", "일일섭취량 : 36정(6.12g)").
1회 2개 이상이면 괄호가 1개 무게인지 1회 총량인지 알 수 없어 쓰지 않는다("1회 2포(2g)"는 1포 무게였다).
개수 단위가 g·ml이면 그 값이 곧 1회 제품량이다("1회 0.45g(0.15g씩 약 3회 분사)").
괄호 안이 수치 하나뿐일 때만 읽는다. "정제 500 mg×2정", "정제 1500mg 3EA", "1정당 500mg"은 쓰지 않는다.
"""

import re
from dataclasses import dataclass

from .units import NUMBER, UNIT, Amount, normalize_text, parse_amounts, to_number

COUNT_UNIT = r"정|캡슐|포|병|스틱|알|환|앰플|개|매|ml|g"
_PAREN = r"\(([^()]*)\)"
_TIMES = re.compile(r"(?:1\s*일|하루)\s*,?\s*(\d+)\s*회")
_PER_TIME = re.compile(rf"(?:1\s*회|회당)\s*(?:{_PAREN}\s*)?(\d+(?:\.\d+)?)\s*({COUNT_UNIT})(?:\s*{_PAREN})?",
                       re.IGNORECASE)
_AFTER_TIMES = re.compile(rf"회\s*,?\s*()(\d+(?:\.\d+)?)\s*({COUNT_UNIT})(?:\s*{_PAREN})?", re.IGNORECASE)
_DAILY_ONLY = re.compile(rf"(?:1\s*일|하루)\s*(\d+(?:\.\d+)?)\s*({COUNT_UNIT})", re.IGNORECASE)
_DAILY_TOTAL = re.compile(r"(?:일일|1\s*일|하루)\s*(?:총\s*)?섭취량\s*[:：]?\s*([^\n]*)")
_BARE_AMOUNT = re.compile(rf"\s*(?:약\s*)?(?:{NUMBER})\s*(?:{UNIT})\s*", re.IGNORECASE)


@dataclass(frozen=True)
class Intake:
    times_per_day: int | None
    count_per_time: float | None
    count_unit: str | None
    product_per_time: Amount | None = None
    product_per_day: Amount | None = None

    @property
    def daily_count(self) -> float | None:
        if self.count_per_time is None:
            return None
        return self.count_per_time * (self.times_per_day or 1)

    @property
    def daily_product(self) -> Amount | None:
        """1일 총량이 적혀 있으면 그 값을 쓴다. 다시 횟수를 곱하지 않는다."""
        if self.product_per_day is not None:
            return self.product_per_day
        if self.product_per_time is None or self.times_per_day is None:
            return None
        return Amount(self.product_per_time.value * self.times_per_day, self.product_per_time.unit)


def parse_intake(text: str | None) -> Intake | None:
    """섭취 횟수·개수를 읽지 못하면 None("건강기능식품 원료로 사용" 등)."""
    text = normalize_text(text)
    times = _TIMES.search(text)
    per_time = _PER_TIME.search(text) or (_AFTER_TIMES.search(text) if times else None)
    daily = None if times or per_time else _DAILY_ONLY.search(text)
    if not times and not per_time and not daily:
        return None
    if per_time:
        count, unit = to_number(per_time[2]), per_time[3].lower()
        if unit in ("g", "ml"):
            product = Amount(count, unit)
        elif count == 1:
            product = _one_product(per_time[1]) or _one_product(per_time[4])
        else:
            product = None
    elif daily:
        count, unit, product = to_number(daily[1]), daily[2].lower(), None
    else:
        count, unit, product = None, None, None
    return Intake(int(times[1]) if times else (1 if daily else None), count, unit, product, _daily_total(text))


def _one_product(inner: str | None) -> Amount | None:
    if not inner or not _BARE_AMOUNT.fullmatch(inner):
        return None
    amounts = _product_amounts(inner)
    return amounts[0] if len(amounts) == 1 else None


def _product_amounts(text: str) -> list[Amount]:
    return [a for a in parse_amounts(text) if a.base()[0] in ("mass", "volume")]


def _daily_total(text: str) -> Amount | None:
    m = _DAILY_TOTAL.search(text)
    if m is None:
        return None
    amounts = _product_amounts(m[1])
    return amounts[0] if len(amounts) == 1 else None
