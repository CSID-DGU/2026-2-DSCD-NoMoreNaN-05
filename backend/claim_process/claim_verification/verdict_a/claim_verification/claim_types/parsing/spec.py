"""BASE_STANDARD(기준 및 규격)에서 성분별 표시량을 읽는다.

    2) 루테인 : 표시량(18.2 mg/0.5g)의 80~120%        → 루테인, 18.2 mg, 0.5 g
    2 구리 : 표시량의 80 ~ 150% (표시량 : 0.465 mg / 2,650 mg)
    2) 프로바이오틱스 수 : 표시량(4,000억 CFU/g) 이상  → 프로바이오틱스, 4000억 CFU, 1 g

80~120% 같은 범위는 품질 규격이라 읽지 않는다. 광고 수치는 표시량 자체와 비교한다.
납·카드뮴처럼 mg/kg로 적는 오염물질 기준은 성분 표시량이 아니므로 버린다.
"""

import re
from dataclasses import dataclass

from .intake import Intake
from .units import (BASIS, NUM_START, NUMBER, UNIT, Amount, comparable, make_basis, make_unit, normalize_text, scaled_number,
                    to_number)

# (3,000억) 같은 괄호 병기와 5μg(200IU)의 IU 병기는 첫 수치와 같은 값이라 지운다.
_PAREN_LARGE = re.compile(rf"\(\s*(?:{NUMBER})\s*(?:억|조|만)\s*(?:cfu)?\s*\)", re.IGNORECASE)
_PAREN_IU = re.compile(rf"\(\s*(?:{NUMBER})\s*iu\s*\)", re.IGNORECASE)
_MARKER = re.compile(r"^\s*(?:\(?\d+(?:-\d+)?[).]|\d+\s+|\d+(?=[가-힣A-Z])|[①-⑳]|[가-힣][.)]\s)\s*")
_FINAL_PRODUCT = re.compile(r"최종\s*제품\s*-?\s*")
_NAME_END = re.compile(r"\s*(?:[(\[{]?\s*표시량|[:：]).*$")
_COUNT_NAME = re.compile(r"\s*(?:수|함량|으로서)$")
# 비타민B1(mg), 헤스페리딘 함량(mg/g) 같은 이름 뒤 단위 표기
_NAME_UNIT = re.compile(r"\s*\(\s*(?:%|(?:mg|μg|ug|mcg|cfu|iu)[^()]*|g(?:\s*/[^()]*)?)\s*\)$", re.IGNORECASE)
# 분모의 "1.000 mg"은 점을 천 단위로 쓴 표기일 수 있어 읽지 않는다. 분자의 "3.840 mg", "0.465 mg"은 소수다.
_DOT_THOUSANDS = re.compile(r"^[1-9]\d{0,2}\.\d{3}$")
_MICROBE_NAME = re.compile(r"균|프로바이오틱스")
_NOT_LABEL = re.compile(r"세균|대장균|^납|카드뮴|수은|비소")
# 분모의 "3, 000 mg". 나열이 올 수 없는 자리라 천 단위로 합친다.
_DENOMINATOR_COMMA = re.compile(r"/\s*(\d{1,3})\s*,\s*(\d{3})(?!\d)")
_PAIR = re.compile(
    rf"{NUM_START}(?P<num>{NUMBER})(?:\s*[xX×]\s*10\^(?P<exp>\d+))?\s*(?P<large>억|조|만)?\s*"
    rf"(?:(?P<unit>{UNIT})(?:\s*(?P<basis>{BASIS})(?![a-z])|(?![a-z])))?\s*/\s*"
    rf"(?:\d+\s*(?:정|캡슐|포)\s*\(\s*)?(?P<per>{NUMBER})?\s*(?P<perunit>{UNIT})(?![a-z])",
    re.IGNORECASE)
# 4 아연(mg/450 mg) : 표시량(2.55)의 80~150%
_UNIT_IN_NAME = re.compile(
    rf"\(\s*(?P<unit>{UNIT})\s*/\s*(?P<per>{NUMBER})?\s*(?P<perunit>{UNIT})\s*\)\s*[:：]\s*"
    rf"표시량\s*[(\[{{]\s*(?P<num>{NUMBER})\s*[)\]}}]",
    re.IGNORECASE)
_LIMIT_UNIT = re.compile(r"/\s*(?:kg|l)\b|/\s*kg", re.IGNORECASE)


@dataclass(frozen=True)
class SpecItem:
    name: str
    amount: Amount
    per: Amount
    line: str


def parse_spec(text: str | None) -> list[SpecItem]:
    items = []
    for line in normalize_text(text).splitlines():
        item = _parse_line(line.strip())
        if item is not None:
            items.append(item)
    return items


def _parse_line(line: str) -> SpecItem | None:
    if not line or _LIMIT_UNIT.search(line) or ("표시량" not in line and "이하" in line):
        return None
    cleaned = _DENOMINATOR_COMMA.sub(r"/\1,\2", _PAREN_IU.sub("", _PAREN_LARGE.sub("", line)))
    m = _UNIT_IN_NAME.search(cleaned)
    if m is not None:
        name = _name(cleaned[:m.start()])
        per = Amount(to_number(m["per"]) if m["per"] else 1.0, make_unit(m["perunit"]))
        if not name or _NOT_LABEL.search(name):
            return None
        if m["per"] and _DOT_THOUSANDS.match(m["per"]) and m["perunit"].lower() == "mg":
            return None
        return SpecItem(name, Amount(to_number(m["num"]), make_unit(m["unit"])), per, line)
    m = _PAIR.search(cleaned)
    if m is None or (not m["unit"] and not m["per"]):
        return None
    name = _name(cleaned[:m.start()])
    if not name or _NOT_LABEL.search(name):
        return None
    if m["per"] and _DOT_THOUSANDS.match(m["per"]) and m["perunit"].lower() == "mg":
        return None
    # 분자 단위가 비어 있으면("1080 /3575mg") 분모 단위와 같은 것으로 읽는다. "1억/2g"은 균수만 받는다.
    if m["large"] and not m["unit"]:
        if not _MICROBE_NAME.search(name):
            return None
        unit = "CFU"
    else:
        unit = make_unit(m["unit"] or m["perunit"])
    value = scaled_number(m["num"], m["exp"], m["large"])
    per = Amount(to_number(m["per"]) if m["per"] else 1.0, make_unit(m["perunit"]))
    amount = Amount(value, unit, make_basis(m["basis"]))
    if comparable(amount, per) and amount.base()[1] > per.base()[1]:
        return None  # 성분량이 제품량보다 많을 수 없다. 분모나 단위를 잘못 적은 줄이다.
    return SpecItem(name, amount, per, line)


def _name(prefix: str) -> str:
    name = _MARKER.sub("", prefix)
    name = _FINAL_PRODUCT.sub("", name)
    name = _NAME_END.sub("", name).strip(" :：-([{")
    return _COUNT_NAME.sub("", _NAME_UNIT.sub("", name))


def daily_amount(item: SpecItem, intake: Intake | None) -> Amount | None:
    """하루 함량 = 표시량 ÷ 제품량 분모 × 하루 제품 섭취량. 하루 제품량을 모르거나 단위가 다르면 None."""
    daily = intake.daily_product if intake else None
    if daily is None or not comparable(item.per, daily) or item.per.value == 0:
        return None
    ratio = daily.base()[1] / item.per.base()[1]
    return Amount(item.amount.value * ratio, item.amount.unit, item.amount.basis)
