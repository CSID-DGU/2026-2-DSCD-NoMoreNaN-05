"""영양성분 이름 통일과 1일 영양성분 기준치.

기준치: 식품 등의 표시·광고에 관한 법률 시행규칙 [별표 5] <개정 2020. 9. 9.>
만 2세 이하 영유아용 식품에는 이 표를 그대로 적용하지 않는다(별표 5 비고 2).

이름은 부분 일치로 찾지 않는다. "비타민B12"가 "비타민B1"로 잡히면 안 된다.
"""

import re

from .units import Amount, normalize_text

DAILY_VALUES: dict[str, Amount] = {
    "탄수화물": Amount(324, "g"), "당류": Amount(100, "g"), "식이섬유": Amount(25, "g"),
    "단백질": Amount(55, "g"), "지방": Amount(54, "g"), "포화지방": Amount(15, "g"),
    "콜레스테롤": Amount(300, "mg"), "나트륨": Amount(2000, "mg"), "칼륨": Amount(3500, "mg"),
    "비타민A": Amount(700, "μg", "RE"), "비타민C": Amount(100, "mg"), "크롬": Amount(30, "μg"),
    "칼슘": Amount(700, "mg"), "철분": Amount(12, "mg"), "비타민D": Amount(10, "μg"),
    "비타민E": Amount(11, "mg", "α-TE"), "비타민K": Amount(70, "μg"), "비타민B1": Amount(1.2, "mg"),
    "비타민B2": Amount(1.4, "mg"), "나이아신": Amount(15, "mg", "NE"), "비타민B6": Amount(1.5, "mg"),
    "엽산": Amount(400, "μg"), "몰리브덴": Amount(25, "μg"), "비타민B12": Amount(2.4, "μg"),
    "바이오틴": Amount(30, "μg"), "판토텐산": Amount(5, "mg"), "인": Amount(700, "mg"),
    "요오드": Amount(150, "μg"), "마그네슘": Amount(315, "mg"), "아연": Amount(8.5, "mg"),
    "셀레늄": Amount(55, "μg"), "구리": Amount(0.8, "mg"), "망간": Amount(3.0, "mg"),
}

_OTHER_NAMES = {
    "탄수화물": ("carbohydrate",), "당류": ("sugars",), "식이섬유": ("dietaryfiber",),
    "단백질": ("protein",), "지방": ("fat",), "나트륨": ("sodium",), "칼륨": ("potassium",),
    "비타민B1": ("티아민", "thiamin", "thiamine"), "비타민B2": ("리보플라빈", "riboflavin"),
    "나이아신": ("니아신", "비타민b3", "vitaminb3", "vitb3", "niacin"),
    "판토텐산": ("비타민b5", "vitaminb5", "vitb5", "pantothenicacid"),
    "비타민B6": ("피리독신", "pyridoxine"), "엽산": ("비타민b9", "vitaminb9", "folicacid", "folate"),
    "비타민C": ("아스코르브산", "ascorbicacid"), "바이오틴": ("비오틴", "biotin", "비타민b7", "vitaminb7"),
    "칼슘": ("calcium", "ca"), "철분": ("철", "iron", "fe"), "마그네슘": ("magnesium", "mg"),
    "아연": ("zinc", "zn"), "셀레늄": ("셀렌", "selenium", "se"), "구리": ("copper", "cu"),
    "망간": ("manganese", "manganes", "mn"), "요오드": ("아이오딘", "iodine"), "몰리브덴": ("molybdenum", "mo"),
    "크롬": ("chromium", "cr"), "인": ("phosphorus",),
}

_NOT_WORD = re.compile(r"[^0-9a-z가-힣]")


def _key(name: str | None) -> str:
    return _NOT_WORD.sub("", normalize_text(name).lower())


def _build_names() -> dict[str, str]:
    names = {}
    for nutrient in DAILY_VALUES:
        names[_key(nutrient)] = nutrient
        if nutrient.startswith("비타민"):
            suffix = nutrient[len("비타민"):].lower()
            names[f"vitamin{suffix}"] = names[f"vit{suffix}"] = nutrient
    for nutrient, others in _OTHER_NAMES.items():
        for other in others:
            names[other] = nutrient
    return names


_NAMES = _build_names()


def canonical(name: str | None) -> str | None:
    """별표 5의 영양성분 이름. 영양성분이 아니면 None."""
    return _NAMES.get(_key(name))


def part_names(name: str | None) -> set[str]:
    """원료명 안에서 찾을 이름들("비오틴 혼합분말"). 두 글자 약어(mg, fe)는 다른 말에 걸리므로 뺀다."""
    nutrient = canonical(name)
    if nutrient is None:
        return set()
    return {key for key, value in _NAMES.items() if value == nutrient and (len(key) >= 3 or not key.isascii())}


def daily_value(name: str | None) -> Amount | None:
    nutrient = canonical(name)
    return DAILY_VALUES[nutrient] if nutrient else None
