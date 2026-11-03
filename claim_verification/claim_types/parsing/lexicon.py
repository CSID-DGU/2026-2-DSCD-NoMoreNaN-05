"""원료명 정규화와 전체 원료 사전(resources/ingredient_lexicon.json).

사전은 "이 이름이 실제 원료 이름인가"를 확인하는 데 쓴다. data.csv의 이명에는 잘못 묶인 값이 있어
("우유" → 소연골분말) 이명을 믿으면 안 된다. 여러 원료에 걸리면 specific이 아니고,
"제품에 없는 원료"로 판정할 수 있는 이름은 대표 이름(is_representative)뿐이다.
"""

import json
import re
from pathlib import Path

from .nutrients import canonical
from .units import normalize_text

LEXICON_PATH = Path(__file__).resolve().parents[2] / "resources" / "ingredient_lexicon.json"

_NOTE = re.compile(r"\([^()]*(?:고시형|\d{4}\s*-\s*\d+\s*호|인정)[^()]*\)")
_MARK = re.compile(r"[™®©]")
_NOT_WORD = re.compile(r"[^0-9a-zα-ω가-힣]")


def strip_note(name: str | None) -> str:
    """(고시형), (제2010-35호) 같은 등록 표기와 ™·®를 지운다."""
    return _NOTE.sub("", normalize_text(_MARK.sub("", name or ""))).strip()


def ingredient_key(name: str | None) -> str:
    """비교용 키. 영양성분은 별표 5 이름으로 모은다("철", "Iron" → "철분")."""
    cleaned = strip_note(name)
    nutrient = canonical(cleaned)
    return _NOT_WORD.sub("", (nutrient or cleaned).lower())


def split_ingredients(text: str | None) -> list[str]:
    """쉼표로 나눈다. 괄호 안 쉼표("식물혼합농축액(대추60%,구기자12%)")에서는 나누지 않는다."""
    parts, depth, current = [], 0, []
    for ch in normalize_text(text):
        depth += ch == "("
        depth -= ch == ")" and depth > 0
        if depth == 0 and ch in ",;\n":
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    parts.append("".join(current))
    return [p.strip() for p in parts if p.strip()]


class Lexicon:
    def __init__(self, terms: dict[str, list[str]]):
        self.terms = terms

    @classmethod
    def load(cls, path: str | Path = LEXICON_PATH) -> "Lexicon":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def lookup(self, name: str | None) -> list[str]:
        return self.terms.get(ingredient_key(name), [])

    def is_specific(self, name: str | None) -> bool:
        return len(self.lookup(name)) == 1

    def is_representative(self, name: str | None) -> bool:
        return ingredient_key(name) in self.lookup(name)
