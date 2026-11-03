"""data.csv → resources/ingredient_lexicon.json. {비교용 키: [대표 원료명, ...]}

    python -m claim_verification.scripts.build_ingredient_lexicon data.csv

대표 이름은 RAWMTRL_STD_INFO의 RAWMTRL_NM과 RAWMTRL_DICT_INFO의 RPRSNT_RAWMTRL_NM이다.
이명은 RAWMTRL_DICT_INFO의 영문명·학명·RAWMTRL_NCKNM이다. 숫자뿐이거나 한 글자인 키는 버린다.
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from ..claim_types.parsing.lexicon import LEXICON_PATH, ingredient_key, split_ingredients, strip_note

csv.field_size_limit(10**9)


def _usable(key: str) -> bool:
    return len(key) >= 2 and not key.isdigit()


def build_terms(rows) -> dict[str, list[str]]:
    terms = defaultdict(set)

    def add(name, representative):
        key = ingredient_key(name)
        if _usable(key):
            terms[key].add(ingredient_key(representative))

    for row in rows:
        for entry in json.loads(row["RAWMTRL_STD_INFO"] or "[]"):
            add(entry["RAWMTRL_NM"], entry["RAWMTRL_NM"])
        for entry in json.loads(row["RAWMTRL_DICT_INFO"] or "[]"):
            representative = strip_note(entry["RPRSNT_RAWMTRL_NM"])
            add(representative, representative)
            for other in [entry["ENG_NM"], entry["SCNM"], *split_ingredients(entry["RAWMTRL_NCKNM"])]:
                add(other, representative)
    return {k: sorted(v) for k, v in sorted(terms.items())}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8-sig", newline="") as f:
        terms = build_terms(csv.DictReader(f))
    Path(LEXICON_PATH).write_text(json.dumps(terms, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(terms)}개 키, 여러 원료에 걸리는 키 {sum(len(v) > 1 for v in terms.values())}개", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
