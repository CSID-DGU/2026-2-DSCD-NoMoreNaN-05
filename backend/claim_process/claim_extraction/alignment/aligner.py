import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from ..common import LLMClient, canon_equal, clean_types, keep, merge_safe, norm, parse_json_object, similarity
from .prompts import (JUDGE_SYSTEM, PRODUCTS_SCHEMA, PRODUCTS_SYSTEM, PRODUCTS_TITLE_RULES, TYPES_SYSTEM,
                      format_judge_input, format_products_input, format_types_input, judge_schema, screens, shown_from,
                      types_schema)
from .schemas import FinalClaim, Product

BRANCH_PRIORITY = ("audio", "text", "scene")    # 대표 멤버 길이가 같을 때 앞쪽 브랜치
VERDICTS = ("SAME", "CONFLICT", "UNRELATED")
_REF = re.compile(r"p\d\d")
COPY_MIN_CHARS = 4         # scene 복사 대조에 쓰는 OCR 줄의 최소 keep 길이
EVIDENCE_SIM = 0.8         # products 이름 ↔ 인용 줄 keep 유사도. 이 이상이면 근거 일치(OCR 교정 허용)
NAME_FIELDS = ("product_ref", "product_name", "brand_name", "manufacturer_name", "manufacturing_report_number")
QUOTES = "'\"‘’“”"


def is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def overlap_ratio(a: dict, b: dict) -> float:
    """겹친 길이 ÷ 짧은 쪽 길이. 9초 음성 안의 0.5초 면책 문구도 1.0이 되도록."""
    inter = min(a["t_end"], b["t_end"]) - max(a["t_start"], b["t_start"])
    shorter = min(a["t_end"] - a["t_start"], b["t_end"] - b["t_start"])
    if shorter <= 0:
        return 1.0 if inter >= 0 else 0.0
    return max(inter, 0.0) / shorter


def lcs_len(x: str, y: str) -> int:
    prev = [0] * (len(y) + 1)
    for cx in x:
        cur = [0]
        for j, cy in enumerate(y, 1):
            cur.append(prev[j - 1] + 1 if cx == cy else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def rouge_l_recall(short: str, long: str) -> float:
    """공백·문장부호 제거 후 글자 단위 ROUGE-L, 짧은 쪽 기준 recall. 기록용."""
    s, l = norm(short), norm(long)
    if len(s) > len(l):
        s, l = l, s
    return lcs_len(s, l) / len(s) if s else 0.0


class UnionFind:
    def __init__(self, ids):
        self.parent = {i: i for i in ids}

    def find(self, x: str) -> str:
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        self.parent[self.find(b)] = self.find(a)

    def members(self, x: str) -> list[str]:
        r = self.find(x)
        return [i for i in self.parent if self.find(i) == r]


class Aligner:
    def __init__(self, llm: LLMClient, overlap_min: float, dedup_sim: float, judge_chunk: int, judge_parallel: int,
                 scene_copy_prefix: re.Pattern, type_chunk: int):
        self.llm = llm
        self.overlap_min = overlap_min
        self.dedup_sim = dedup_sim
        self.judge_chunk = judge_chunk
        self.judge_parallel = judge_parallel
        self.scene_copy_prefix = scene_copy_prefix
        self.type_chunk = type_chunk

    # ── 0. scene 글자 복사 제거 ──────────────────────────
    def drop_scene_copies(self, data: dict) -> tuple[list[dict], list[dict]]:
        """서술 접두어·따옴표를 뗀 scene 문장이 그 프레임 시각에 보였을 OCR 줄과 정규형 일치하고,
        그 줄과 정규형 일치하는 text Claim이 있으면 제거. (남길 scene Claim, 제거 기록)"""
        spans = data["text"]["screen_texts"]
        tclaims = data["text"]["claims"]
        kept, dropped = [], []
        for s in data["scene"]["claims"]:
            core = self.scene_copy_prefix.sub("", s["text"].strip(), count=1).strip().strip(QUOTES).strip()
            f = s["t_start"]
            hit = next((p for p in spans
                        if shown_from(p) <= f < p["t_end"] and len(keep(p["text"])) >= COPY_MIN_CHARS
                        and canon_equal(core, p["text"]) and any(canon_equal(t["text"], p["text"]) for t in tclaims)),
                       None)
            if hit is None:
                kept.append(s)
                continue
            print(f"  [dup-ocr] {s['claim_id']} ⟷ span {hit['span_id']}")
            dropped.append({"scene": s["claim_id"], "span": hit["span_id"], "text": s["text"]})
        return kept, dropped

    # ── 1. 시간 후보: 우선순위 높은 브랜치 H × 낮은 브랜치 L ──
    def candidates(self, claims: dict[str, list[dict]]) -> list[tuple[str, dict, str, dict, float]]:
        branches = [b for b in BRANCH_PRIORITY if b in claims]
        pairs = []
        for i, hb in enumerate(branches):
            for lb in branches[i + 1:]:
                for l in claims[lb]:
                    for h in claims[hb]:
                        r = overlap_ratio(h, l)
                        if r >= self.overlap_min:
                            pairs.append((hb, h, lb, l, r))
        return pairs

    # ── 5. SAME / CONFLICT / UNRELATED (judge_chunk쌍씩 묶어 judge_parallel개 동시 호출) ──
    def judge_chunk_call(self, k: int, n_chunks: int, pairs: list[tuple[str, str, dict, str, dict]]) -> list[str | None]:
        """묶음 하나(번호 0..n-1). 파싱·구조 실패는 그 묶음만 None, 재시도 없음."""
        n = len(pairs)
        verdicts: list[str | None] = [None] * n
        raw = self.llm.chat(JUDGE_SYSTEM, format_judge_input(pairs), schema=judge_schema(n))
        try:
            out = parse_json_object(raw)
            rows = out.get("verdicts") if isinstance(out, dict) else None
            if not isinstance(rows, list) or not all(
                    isinstance(v, dict) and isinstance(v.get("pair"), int) and not isinstance(v.get("pair"), bool)
                    and isinstance(v.get("verdict"), str) for v in rows):
                raise ValueError(f"verdicts 구조 오류: {raw[:200]!r}")
        except ValueError as e:
            print(f"  [skip] 판정 묶음 {k}/{n_chunks} ({n}쌍): {e}")
            return verdicts
        seen: Counter = Counter()
        bad = 0
        for v in rows:
            i = v["pair"]
            if 0 <= i < n:
                verdicts[i] = v["verdict"]          # 중복이면 마지막 값
                seen[i] += 1
                bad += v["verdict"] not in VERDICTS
        missing = sum(seen[i] == 0 for i in range(n))
        dup = sum(seen[i] >= 2 for i in range(n))
        if missing or dup or bad:
            print(f"  [warn] 판정 묶음 {k}/{n_chunks}: 누락 {missing}, 중복 {dup}, 값 오류 {bad}")
        return verdicts

    def judge(self, pairs: list[tuple[str, str, dict, str, dict]]) -> list[str | None]:
        """pairs: (kind, A 브랜치, A, B 브랜치, B). 순서대로 judge_chunk개씩 자르고(마지막만 짧음) 묶음 순서로 이어 붙인다."""
        if not pairs:
            return []
        chunks = [pairs[i:i + self.judge_chunk] for i in range(0, len(pairs), self.judge_chunk)]
        print(f"  판정 {len(pairs)}쌍 → {len(chunks)}묶음(≤{self.judge_chunk}쌍), 병렬 {self.judge_parallel}", flush=True)
        with ThreadPoolExecutor(max_workers=self.judge_parallel) as pool:
            futures = [pool.submit(self.judge_chunk_call, k, len(chunks), c) for k, c in enumerate(chunks, 1)]
            return [v for f in futures for v in f.result()]

    # ── 7-1. 최종 Claim 유형 (type_chunk건씩 묶어 judge_parallel개 동시 호출) ──
    def type_chunk_call(self, k: int, n_chunks: int, texts: list[str]) -> list[list[str] | None]:
        """묶음 하나(번호 0..n-1). 호출·파싱·구조 실패는 그 묶음만 None, 재시도 없음."""
        n = len(texts)
        types: list[list[str] | None] = [None] * n
        try:
            raw = self.llm.chat(TYPES_SYSTEM, format_types_input(texts), schema=types_schema(n))
            out = parse_json_object(raw)
            rows = out.get("types") if isinstance(out, dict) else None
            if not isinstance(rows, list) or not all(
                    isinstance(v, dict) and is_int(v.get("claim")) and isinstance(v.get("claim_type"), list)
                    for v in rows):
                raise ValueError(f"types 구조 오류: {raw[:200]!r}")
        except (OSError, ValueError) as e:
            print(f"  [skip] 유형 묶음 {k}/{n_chunks} ({n}건): {e}")
            return types
        seen: Counter = Counter()
        for v in rows:
            i = v["claim"]
            if 0 <= i < n:
                types[i] = clean_types(v["claim_type"]) or None          # 중복이면 마지막 값
                seen[i] += 1
        missing = sum(seen[i] == 0 for i in range(n))
        dup = sum(seen[i] >= 2 for i in range(n))
        bad = sum(seen[i] > 0 and types[i] is None for i in range(n))
        if missing or dup or bad:
            print(f"  [warn] 유형 묶음 {k}/{n_chunks}: 누락 {missing}, 중복 {dup}, 값 오류 {bad}")
        return types

    def retype(self, final: list[FinalClaim]) -> dict[str, str]:
        """최종 Claim의 claim_type을 LLM 값으로 덮어쓴다. 실패한 자리는 대표 멤버 값 그대로. {claim_id: llm | member}"""
        if not final:
            return {}
        chunks = [final[i:i + self.type_chunk] for i in range(0, len(final), self.type_chunk)]
        print(f"  유형 {len(final)}건 → {len(chunks)}묶음(≤{self.type_chunk}건), 병렬 {self.judge_parallel}", flush=True)
        with ThreadPoolExecutor(max_workers=self.judge_parallel) as pool:
            futures = [pool.submit(self.type_chunk_call, k, len(chunks), [c.text for c in ch])
                       for k, ch in enumerate(chunks, 1)]
            types = [t for f in futures for t in f.result()]
        source = {}
        for c, t in zip(final, types):
            if t:
                c.claim_type = t
            source[c.claim_id] = "llm" if t else "member"
        return source

    # ── 8. products (LLM 1회) ──────────────────────────
    def products(self, data: dict, claims: list[FinalClaim],
                 title: str | None = None) -> tuple[list[Product], dict, list[dict]]:
        """(products, claim_products, products_evidence). 파싱·구조 실패는 ([], {}, []). title이 있으면 제목 규칙을 붙인다."""
        system = PRODUCTS_SYSTEM + ("\n" + PRODUCTS_TITLE_RULES if title else "")
        raw = self.llm.chat(system, format_products_input(data, [(c.claim_id, c.text) for c in claims], title),
                            schema=PRODUCTS_SCHEMA)
        try:
            out = parse_json_object(raw)
            items = out.get("products") if isinstance(out, dict) else None
            mapping = out.get("claim_products", {}) if isinstance(out, dict) else None
            if not isinstance(items, list) or not isinstance(mapping, dict) or not all(
                    isinstance(p, dict) and isinstance(p.get("evidence"), dict)
                    and all(isinstance(p["evidence"].get(f), list) and all(is_int(i) for i in p["evidence"][f])
                            for f in ("product_name", "brand_name"))
                    and all(p.get(f) is None or isinstance(p.get(f), str) for f in NAME_FIELDS)
                    for p in items):
                raise ValueError(f"products 구조 오류: {raw[:200]!r}")
        except ValueError as e:
            print(f"  [skip] products: {e}")
            return [], {}, []
        products = [Product(p.get("product_ref"), p.get("product_name"), p.get("brand_name"),
                            p.get("manufacturer_name"), p.get("manufacturing_report_number"))
                    for p in items]
        return products, mapping, self.check_evidence(data, items, title)

    @staticmethod
    def check_evidence(data: dict, items: list[dict], title: str | None = None) -> list[dict]:
        """이름 표기의 출처만 검증(값은 바꾸지 않음). 역할(브랜드인지)은 검증하지 않는다."""
        spans = {s["span_id"]: s["text"] for s in screens(data)}
        script = keep(" ".join(s["text"] for s in (data["audio"]["transcript"] if "audio" in data else []))).lower()
        records = []
        for p in items:
            for f in ("product_name", "brand_name"):
                name, ids = p.get(f), p["evidence"][f]
                if name is None:
                    verdict = "ok" if not ids else "unneeded"
                    if ids:
                        print(f"  [warn] products 근거 불필요: {f} null ← spans {ids}")
                elif not ids:
                    if title and keep(name).lower() in keep(title).lower():
                        verdict = "title"
                        print(f"  [info] products 제목 출처: {f} {name!r}")
                    elif keep(name).lower() in script:
                        verdict = "audio"
                        print(f"  [info] products 음성 출처: {f} {name!r}")
                    else:
                        verdict = "none"
                        print(f"  [warn] products 근거 없음: {f} {name!r}")
                elif bad := [i for i in ids if i not in spans]:
                    verdict = "bad_id"
                    print(f"  [warn] products 근거 번호 없음: {f} {bad}")
                else:
                    k = keep(name).lower()
                    cited = [keep(spans[i]).lower() for i in ids]
                    if similarity(k, "".join(cited)) >= EVIDENCE_SIM or any(similarity(k, c) >= EVIDENCE_SIM for c in cited):
                        verdict = "ok"
                    else:
                        verdict = "mismatch"
                        print(f"  [warn] products 근거 불일치: {f} {name!r} ← spans {ids}")
                records.append({"product_ref": p.get("product_ref"), "field": f, "name": name, "evidence": ids,
                                "verdict": verdict})
        return records

    # ── 전체 ────────────────────────────────────────────
    def align(self, data: dict, title: str | None = None) -> tuple[list[Product], list[FinalClaim], dict]:
        """data: 브랜치 → 브랜치 파일 내용. (products, 최종 Claim, alignment 기록)"""
        # 0. scene 글자 복사 제거 (text 브랜치가 있을 때만). 제거된 scene은 이후 단계·products 입력에 안 들어감
        dropped_scene = []
        if "scene" in data and "text" in data:
            kept, dropped_scene = self.drop_scene_copies(data)
            data = {**data, "scene": {**data["scene"], "claims": kept}}
        claims = {b: data[b]["claims"] for b in BRANCH_PRIORITY if b in data}
        by_id = {c["claim_id"]: c for cs in claims.values() for c in cs}
        branch_of = {c["claim_id"]: b for b, cs in claims.items() for c in cs}

        def rank(cid: str) -> tuple[int, int]:
            """대표 멤버: 가장 긴 text, 같으면 우선순위 높은 브랜치."""
            return len(keep(by_id[cid]["text"])), -BRANCH_PRIORITY.index(branch_of[cid])

        # 1·2. 시간 후보 중 정규형 일치만 자동 병합(RULE)
        time_pairs = self.candidates(claims)
        rule_edges = [(h["claim_id"], l["claim_id"]) for _, h, _, l, _ in time_pairs
                      if canon_equal(h["text"], l["text"])]
        rule_set = set(rule_edges)

        # 3. 잠정 그룹
        tent = UnionFind(by_id)
        for a, b in rule_edges:
            tent.union(a, b)

        # 4. 전역 후보: 서로 다른 잠정 그룹 대표끼리 keep 유사도
        reps = list(dict.fromkeys(max(tent.members(c), key=rank) for c in by_id))
        timed = {frozenset((h["claim_id"], l["claim_id"])) for _, h, _, l, _ in time_pairs}
        global_pairs = []
        for i, a in enumerate(reps):
            for b in reps[i + 1:]:
                if similarity(keep(by_id[a]["text"]), keep(by_id[b]["text"])) < self.dedup_sim:
                    continue
                if canon_equal(by_id[a]["text"], by_id[b]["text"]):
                    rule_edges.append((a, b))
                    rule_set.add((a, b))
                elif frozenset((a, b)) not in timed:
                    global_pairs.append((a, b))

        # 5. LLM 판정(묶음·병렬): RULE 아닌 시간 후보 + 전역 후보
        judge_pairs = [("time", h["claim_id"], l["claim_id"], r) for _, h, _, l, r in time_pairs
                       if (h["claim_id"], l["claim_id"]) not in rule_set]
        judge_pairs += [("global", a, b, overlap_ratio(by_id[a], by_id[b])) for a, b in global_pairs]
        verdicts = self.judge([(k, branch_of[a], by_id[a], branch_of[b], by_id[b]) for k, a, b, _ in judge_pairs])

        # 6. CONFLICT 등록 → RULE 재검사 → SAME 병합(merge_safe + cannot-link)
        cannot = {frozenset((a, b)) for (_, a, b, _), v in zip(judge_pairs, verdicts) if v == "CONFLICT"}
        uf = UnionFind(by_id)
        outcome: dict[tuple[str, str], str] = {}

        def linkable(a: str, b: str) -> bool:
            ga, gb = uf.members(a), uf.members(b)
            return not any(frozenset((x, y)) in cannot for x in ga for y in gb)

        for a, b in rule_edges:
            if linkable(a, b):
                uf.union(a, b)
                outcome[(a, b)] = "RULE"
            else:
                outcome[(a, b)] = "LINK_BLOCKED"
        same = [(r, similarity(keep(by_id[a]["text"]), keep(by_id[b]["text"])), a, b)
                for (_, a, b, r), v in zip(judge_pairs, verdicts) if v == "SAME"]
        for _, _, a, b in sorted(same, key=lambda s: (s[0], s[1]), reverse=True):
            if not merge_safe(by_id[a]["text"], by_id[b]["text"]):
                outcome[(a, b)] = "SAME_BLOCKED"
            elif uf.find(a) != uf.find(b) and not linkable(a, b):
                outcome[(a, b)] = "LINK_BLOCKED"
            else:
                uf.union(a, b)

        # 7. 그룹 → 최종 Claim. 대표 멤버가 text·claim_type, 나머지 필드는 대표 → 브랜치 우선순위 순으로 첫 값
        groups: dict[str, list[str]] = {}
        for cid in by_id:                                   # 브랜치 우선순위 순
            groups.setdefault(uf.find(cid), []).append(cid)
        rows = []
        for ids in groups.values():
            rep = max(ids, key=rank)
            ms = [by_id[rep]] + [by_id[c] for c in ids if c != rep]
            ingredients: list[str] = []
            for m in ms:
                ingredients += [x for x in m["ingredients"] if x not in ingredients]
            first = lambda f: next((m[f] for m in ms if m.get(f) is not None), None)   # noqa: E731
            rows.append((ms, FinalClaim(
                claim_id="", product_ref=None, text=ms[0]["text"], claim_type=ms[0]["claim_type"],
                ingredients=ingredients, effect=first("effect"), quantity=first("quantity"),
                intake_basis=first("intake_basis"),
                t_start=min(m["t_start"] for m in ms), t_end=max(m["t_end"] for m in ms),
            )))
        rows.sort(key=lambda r: (r[1].t_start, r[1].t_end))

        final_of: dict[str, str] = {}
        members: dict[str, dict[str, list[str]]] = {}
        for n, (ms, c) in enumerate(rows):
            c.claim_id = f"c{n + 1:02d}"
            members[c.claim_id] = {b: [m["claim_id"] for m in ms if branch_of[m["claim_id"]] == b] for b in claims}
            for m in ms:
                final_of[m["claim_id"]] = c.claim_id
        final = [c for _, c in rows]
        type_source = self.retype(final)

        records, conflicts = [], []
        for (kind, a, b, r), v in zip(judge_pairs, verdicts):
            records.append({"h": a, "l": b, "kind": kind, "overlap": round(r, 3),
                            "rouge": round(rouge_l_recall(by_id[a]["text"], by_id[b]["text"]), 3),
                            "verdict": outcome.get((a, b), v)})
            if v == "CONFLICT" and final_of[a] != final_of[b]:
                conflicts.append([final_of[a], final_of[b]])
        for a, b in rule_edges:
            records.append({"h": a, "l": b, "kind": "time" if frozenset((a, b)) in timed else "global",
                            "overlap": round(overlap_ratio(by_id[a], by_id[b]), 3),
                            "rouge": round(rouge_l_recall(by_id[a]["text"], by_id[b]["text"]), 3),
                            "verdict": outcome[(a, b)]})

        products, mapping, evidence = self.products(data, final, title)
        refs = {p.product_ref for p in products}
        for c in final:
            ref = mapping.get(c.claim_id)
            if ref is not None and not (isinstance(ref, str) and _REF.fullmatch(ref) and ref in refs):
                print(f"  [warn] product_ref 매핑 불가 → null: {c.claim_id} {ref!r}")
                ref = None
            c.product_ref = ref
        # 제품이 하나면 모든 Claim은 그 제품 (null·매핑 불가 보정)
        only = products[0].product_ref if len(products) == 1 else None
        if isinstance(only, str) and _REF.fullmatch(only):
            fixed = [c for c in final if c.product_ref is None]
            for c in fixed:
                c.product_ref = only
            if fixed:
                print(f"  [info] product_ref 보정 {len(fixed)}건 → {only}")

        n = {v: sum(r["verdict"] == v for r in records)
             for v in ("RULE", "SAME", "CONFLICT", "SAME_BLOCKED", "LINK_BLOCKED")}
        print(f"  시간 후보 {len(time_pairs)}, 전역 후보 {len(global_pairs)}, LLM 판정 {len(judge_pairs)}, "
              + ", ".join(f"{k} {v}" for k, v in n.items()) + f", 최종 {len(final)}")
        record = {"branches": list(claims), "pairs": records, "conflicts": conflicts, "claims": members,
                  "type_source": type_source, "dropped_scene": dropped_scene, "products_evidence": evidence}
        return products, final, record
