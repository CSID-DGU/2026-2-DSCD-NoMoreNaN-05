"""클레임 문장에서 질병·증상 명칭 후보를 찾는다.

사전(resources/disease_terms.json)을 집합으로 올려 두고, 문장을 Kiwi로 나눈 명사 묶음과 맞춘다.
글자 포함 여부로 찾으면 "콜마비앤에이치"→마비, "최수종"→수종처럼 단어 속 글자에 걸린다.
그래서 명사 경계에서 시작하고 끝나는 것만 인정한다.
예외로 일반명사(NNG) 하나 안에서 앞이나 끝에 붙은 명칭("암세포", "항암")은 partial로 표시해 남긴다.
남은 조각도 일반명사여야 한다("세포", "항"). "카르복시"의 "카르"는 일반명사가 아니라 "복시"를 잡지 않는다.
고유명사(NNP: 회사·사람 이름)는 안을 들여다보지 않는다.

이건 판정이 아니라 후보 탐지다. 예방·치료 주장인지는 조항(NLI)이 정한다.
"""

import json
from functools import lru_cache
from pathlib import Path

TERMS_PATH = Path(__file__).resolve().parent / "resources/disease_terms.json"

NOUN_TAGS = ("NNG", "NNP", "SL", "SN")
# Kiwi가 "다낭성난소증후군"을 "다낭성"+"난소"+"증후군"처럼 나눠도 다시 붙여 본다.
MAX_SPAN = 4


@lru_cache(maxsize=1)
def _terms() -> dict[str, dict]:
    data = json.loads(TERMS_PATH.read_text(encoding="utf-8"))
    return {t["term"]: t for t in data["terms"]}


@lru_cache(maxsize=1)
def _plain_kiwi():
    """사용자 단어를 등록하지 않은 Kiwi. 조각이 원래 무슨 품사인지 볼 때 쓴다."""
    from kiwipiepy import Kiwi

    return Kiwi()


@lru_cache(maxsize=1)
def _kiwi():
    from kiwipiepy import Kiwi

    plain, kiwi = _plain_kiwi(), Kiwi()
    # Kiwi가 명사가 아닌 조각으로 나누는 명칭만 알려 준다 ("이명"→관형사 "이"+"명").
    # 명사 여러 개로 나뉘는 명칭은 find()가 다시 붙여 찾으니 등록하지 않는다.
    # 전부 등록하면 "카르복시메틸셀룰로스"를 "카르"+"복시"로 쪼개 질병명(복시)을 만들어 낸다.
    for term in _terms():
        if len(term) >= 2 and not _all_nouns(plain, term):
            kiwi.add_user_word(term, "NNG")
    return kiwi


def _all_nouns(kiwi, word: str) -> bool:
    return all(t.tag in NOUN_TAGS for t in kiwi.tokenize(word))


def find(text: str, kinds: tuple[str, ...] = ("disease",)) -> list[dict]:
    """[{"term", "kind", "ambiguous", "partial", "start", "end"}]. 겹치면 긴 명칭을 남긴다."""
    terms = _terms()
    # 해시태그("#탈모예방")는 Kiwi가 통째로 태그 처리해 명사가 나오지 않는다.
    tokens = _kiwi().tokenize(text.replace("#", " "))
    found = []
    for run in _noun_runs(tokens):
        for i in range(len(run)):
            for j in range(i + 1, min(i + MAX_SPAN, len(run)) + 1):
                word = "".join(t.form for t in run[i:j]).replace(" ", "")
                t = terms.get(word)
                if t and t["kind"] in kinds:
                    found.append(_hit(t, run[i].start, run[j - 1].end, partial=False))
        for tok in run:
            if tok.tag == "NNG" and tok.form not in terms:
                found.extend(_affix_hits(tok, terms, kinds))
    return _longest(found)


def _affix_hits(tok, terms: dict, kinds: tuple[str, ...]) -> list[dict]:
    hits = []
    for k in range(1, len(tok.form)):
        head, tail = tok.form[:k], tok.form[k:]
        for word, rest, start, end in ((head, tail, tok.start, tok.start + k),
                                       (tail, head, tok.start + k, tok.end)):
            t = terms.get(word)
            if t and t["kind"] in kinds and _common_noun(rest):
                hits.append(_hit(t, start, end, partial=True))
    return hits


@lru_cache(maxsize=4096)
def _common_noun(word: str) -> bool:
    tokens = _plain_kiwi().tokenize(word)
    return len(tokens) == 1 and tokens[0].tag == "NNG"


def _hit(t: dict, start: int, end: int, partial: bool) -> dict:
    return {"term": t["term"], "kind": t["kind"], "ambiguous": t["ambiguous"], "partial": partial,
            "start": start, "end": end}


def _noun_runs(tokens) -> list[list]:
    """띄어쓰기 없이 붙어 있는 명사끼리 묶는다."""
    runs, run = [], []
    for t in tokens:
        if t.tag in NOUN_TAGS and (not run or run[-1].end == t.start):
            run.append(t)
            continue
        if run:
            runs.append(run)
        run = [t] if t.tag in NOUN_TAGS else []
    if run:
        runs.append(run)
    return runs


def _longest(found: list[dict]) -> list[dict]:
    kept = []
    for f in sorted(found, key=lambda f: (f["start"], -(f["end"] - f["start"]))):
        if kept and f["start"] < kept[-1]["end"]:
            continue
        kept.append(f)
    return kept
