"""영상 표기(제목·화면 글자·음성)를 식약처 DB 제품·회사 표기에서 글자 그대로 찾아 products 프롬프트의 역할 참고 줄로 만든다."""
import bisect
import re
import unicodedata
from collections import Counter, defaultdict

import psycopg
from psycopg.rows import dict_row

from claim_process.claim_verification.product_mapping.scripts.recover_product_candidates import RecoveryIndex
from claim_process.claim_verification.product_mapping.src.claim_evidence_experiment import name_key
from claim_process.claim_verification.product_mapping.src.product_identity_filtered import (FilteredProductCatalog,
                                                                                            company_core)

from .prompts import screens

COMPANY_MIN_CHARS = 2      # 회사명 조회 조각의 최소 글자 수
PREFIX_MIN_CHARS = 3       # 제품명 앞부분 조회 조각의 최소 글자 수
SHORT_LINE_TOKENS = 3      # 제품명 앞부분을 조회하는 화면 줄의 최대 토큰 수
EXAMPLES = 3               # 줄마다 보여 주는 회사·제품 예시 수
HINT_MAX_ROWS = 30

_CORP = re.compile(r"\(\s*주\s*\)|㈜|주식회사|\(\s*유\s*\)|유한회사")
_TOKEN = re.compile(r"[가-힣A-Za-z0-9]+")
KINDS = ("A", "B", "C")


def pieces(line: str) -> tuple[list[tuple[str, str]], int]:
    """법인 표기를 지우고 토큰으로 나눈 뒤 연속 토큰 1~3개를 이은 조각. ([(키, 원문 표기)], 토큰 수)"""
    text = unicodedata.normalize("NFC", line)
    tokens = list(_TOKEN.finditer(_CORP.sub(lambda m: " " * len(m.group()), text)))
    out = []
    for i in range(len(tokens)):
        for j in range(i, min(i + 3, len(tokens))):
            out.append(("".join(t.group().casefold() for t in tokens[i:j + 1]),
                        text[tokens[i].start():tokens[j].end()]))
    return out, len(tokens)


class NameHints:
    def __init__(self, products: list[dict], ingredient_names: list[str]):
        self.index = RecoveryIndex(products, ingredient_names)
        self.generic = self.index.generic
        self.names = defaultdict(list)
        self.companies = defaultdict(list)
        labels = defaultdict(Counter)
        for p in products:
            self.names[name_key(p["product_name"])].append(p)
            core = company_core(p["company_name"])
            if core:
                self.companies[core].append(p)
                labels[core][p["company_name"]] += 1
        self.label = {core: c.most_common(1)[0][0] for core, c in labels.items()}
        ordered = sorted(products, key=lambda p: name_key(p["product_name"]))
        self.sorted_keys = [name_key(p["product_name"]) for p in ordered]
        self.sorted_rows = ordered

    @classmethod
    def from_db(cls, dsn: str) -> "NameHints":
        with psycopg.connect(dsn, autocommit=True, row_factory=dict_row) as db:
            products = FilteredProductCatalog(db).products
            ingredients = [r["ingredient_name"] for r in
                           db.execute("SELECT ingredient_name FROM ingredients ORDER BY ingredient_id")]
        return cls(products, ingredients)

    def company_list(self, rows: list[dict]) -> list[str]:
        counts = Counter(company_core(p["company_name"]) for p in rows)
        return [self.label.get(core, core) for core, _ in counts.most_common() if core]

    def describe(self, kind: str, rows: list[dict]) -> str:
        if kind == "A":
            core = company_core(rows[0]["company_name"])
            return f"DB 회사명 ({self.label[core]}, 제품 {len(rows)}건)"
        companies = self.company_list(rows)
        if kind == "B":
            return f"DB 제품명과 같음 (회사: {', '.join(companies[:EXAMPLES])})"
        examples = list(dict.fromkeys(p["product_name"] for p in rows))[:EXAMPLES]
        return (f"DB 제품명 {len(rows)}건이 이 표기로 시작 (예: {', '.join(examples)} / "
                f"회사 {len(companies)}곳: {', '.join(companies[:EXAMPLES])})")

    def rows(self, data: dict, title: str | None) -> list[str]:
        lines = [("제목", None, title)] if title else []
        lines += [("화면", s["span_id"], s["text"]) for s in screens(data)]
        lines += [("음성", None, s["text"]) for s in (data["audio"]["transcript"] if "audio" in data else [])]

        found: dict[str, dict] = {}

        def hit(key: str, text: str, source: tuple, kind: str, rows: list[dict]) -> None:
            r = found.setdefault(key, {"text": text, "sources": set(), "kinds": {}})
            r["sources"].add(source)
            r["kinds"][kind] = rows

        for where, span, line in lines:
            source = (where, span)
            parts, n_tokens = pieces(line)
            short = where == "제목" or (where == "화면" and n_tokens <= SHORT_LINE_TOKENS)
            for key, text in parts:
                if len(key) >= COMPANY_MIN_CHARS and key in self.companies:
                    hit(key, text, source, "A", self.companies[key])
                if short and len(key) >= PREFIX_MIN_CHARS and key not in self.generic:
                    lo = bisect.bisect_right(self.sorted_keys, key)
                    hi = bisect.bisect_left(self.sorted_keys, key + "\U0010ffff")
                    if hi > lo:
                        hit(key, text, source, "C", self.sorted_rows[lo:hi])
            whole = name_key(line)
            if whole in self.names and whole not in self.generic:
                hit(whole, line.strip(), source, "B", self.names[whole])
            for p in self.index.context_products(line):
                k = name_key(p["product_name"])
                hit(k, p["product_name"], source, "B", self.names[k])

        for kind in KINDS:
            have = [(k, {p["product_id"] for p in r["kinds"][kind]}) for k, r in found.items() if kind in r["kinds"]]
            for k, ids in have:
                if any(len(k2) > len(k) and k in k2 and ids <= ids2 for k2, ids2 in have):
                    del found[k]["kinds"][kind]

        ordered = sorted((kr for kr in found.items() if kr[1]["kinds"]),
                         key=lambda kr: (min(KINDS.index(x) for x in kr[1]["kinds"]), -len(kr[0])))
        out = []
        for _, r in ordered:
            wheres = {w for w, _ in r["sources"]}
            spans = sorted(s for w, s in r["sources"] if w == "화면")
            src = (["제목"] if "제목" in wheres else []) + (["화면 " + "".join(f"({i})" for i in spans)] if spans else []) \
                + (["음성"] if "음성" in wheres else [])
            desc = "; ".join(self.describe(x, r["kinds"][x]) for x in KINDS if x in r["kinds"])
            out.append(f'- "{r["text"]}" [{", ".join(src)}] → {desc}')
        if len(out) > HINT_MAX_ROWS:
            return out[:HINT_MAX_ROWS] + [f"(이하 {len(out) - HINT_MAX_ROWS}줄 생략)"]
        return out
