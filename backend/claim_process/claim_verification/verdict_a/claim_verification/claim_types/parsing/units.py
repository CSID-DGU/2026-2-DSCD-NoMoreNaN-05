"""숫자·단위 읽기. 질량은 μg, 균수는 CFU, 부피는 mL로 맞춰 비교한다.

basis는 RE·RAE·α-TE·NE·DFE 같은 환산 기준이다. 둘 다 적혀 있는데 다르면 비교할 수 없다.
"""

import re
import unicodedata
from dataclasses import dataclass

_SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

MASS = {"g": 1e6, "mg": 1e3, "μg": 1.0}
VOLUME = {"l": 1e3, "ml": 1.0}
_UNIT_ALIASES = {"ug": "μg", "mcg": "μg", "cfu": "CFU", "iu": "IU", "마리": "CFU"}

NUMBER = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
UNIT = r"mg|μg|ug|mcg|kcal|cfu|iu|ml|g|l|마리"
BASIS = r"[αa]-?te|rae|re|ne|dfe"
# 지수 표기의 꼬리(2.0E+11의 11, 10^-3의 3)나 쉼표 뒤 조각(3, 000의 000)을 독립 수치로 읽지 않는다.
# "50, 100, 200 mg"처럼 나열일 수 있어 쉼표 뒤 공백은 천 단위로 합치지 않고 읽지 않는 쪽을 택한다.
NUM_START = r"(?<![\d.,^])(?<!\^-)(?<![\d.][eE])(?<![\d.][eE][+-])(?<!\d,\s)(?<!\d\s,)"
LARGE = {"억": 1e8, "조": 1e12, "만": 1e4}
_AMOUNT = re.compile(
    rf"{NUM_START}(?P<num>{NUMBER})\s*(?:[xX×]\s*10\^(?P<exp>\d+)\s*)?(?P<large>억|조|만)?\s*"
    rf"(?P<unit>{UNIT})(?:\s*(?P<basis>{BASIS})(?![a-z])|(?![a-z]))",
    re.IGNORECASE)


@dataclass(frozen=True)
class Amount:
    value: float
    unit: str
    basis: str | None = None

    def base(self) -> tuple[str, float]:
        """(차원, 기준 단위 값)."""
        if self.unit in MASS:
            return "mass", self.value * MASS[self.unit]
        if self.unit in VOLUME:
            return "volume", self.value * VOLUME[self.unit]
        return self.unit, self.value


def normalize_text(text: str | None) -> str:
    """전각·㎎·₁ 같은 표기를 통일한다. 위 첨자 지수(10⁸)는 숫자와 붙지 않게 10^8로 바꾼다."""
    text = re.sub(r"10([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", lambda m: "10^" + m.group(1).translate(_SUPERSCRIPT), text or "")
    return unicodedata.normalize("NFKC", text)


def to_number(text: str) -> float:
    return float(text.replace(",", ""))


def scaled_number(num: str, exp: str | None = None, large: str | None = None) -> float:
    """"2.7" + 지수 11 → 2.7e11. 소수 오차가 생기지 않게 문자열로 지수를 붙인다."""
    value = float(f"{num.replace(',', '')}e{exp or 0}")
    return value * LARGE[large] if large else value


def make_unit(text: str) -> str:
    low = text.lower()
    return _UNIT_ALIASES.get(low, low)


def make_basis(text: str | None) -> str | None:
    if not text:
        return None
    low = text.lower().replace("-", "")
    return "α-TE" if low in ("αte", "ate") else low.upper()


def parse_amounts(text: str | None) -> list[Amount]:
    """문장 속 수치를 순서대로 읽는다. 단위가 없는 숫자는 읽지 않는다."""
    out = []
    for m in _AMOUNT.finditer(normalize_text(text)):
        out.append(Amount(scaled_number(m["num"], m["exp"], m["large"]), make_unit(m["unit"]), make_basis(m["basis"])))
    return out


def comparable(a: Amount, b: Amount) -> bool:
    if a.base()[0] != b.base()[0]:
        return False
    return a.basis is None or b.basis is None or a.basis == b.basis


def same_amount(a: Amount, b: Amount, tolerance: float = 0.01) -> bool:
    """비교할 수 있는 두 수치가 허용 오차 안에서 같은가. 먼저 comparable을 확인한다."""
    x, y = a.base()[1], b.base()[1]
    if y == 0:
        return x == 0
    return abs(x - y) / abs(y) <= tolerance
