import re

from .llm import LLMClient
from .prompts import (CONFLICT_SYSTEM, PRODUCT_SYSTEM, format_conflict_input,
                     format_product_input, parse_json_object)
from .schemas import AlignedClaim

_STRIP = re.compile(r"[\s.,!?~·'\"“”‘’()\[\]-]")


def _norm(s: str) -> str:
    return _STRIP.sub("", s)


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
    """공백·문장부호 제거 후 글자 단위 ROUGE-L, 짧은 쪽 기준 recall."""
    s, l = _norm(short), _norm(long)
    if len(s) > len(l):
        s, l = l, s
    return lcs_len(s, l) / len(s) if s else 0.0


class Aligner:
    def __init__(self, llm: LLMClient, overlap_min: float, rouge_min: float,
                 min_chars: int, deictic: tuple[str, ...]):
        self.llm = llm
        self.overlap_min = overlap_min
        self.rouge_min = rouge_min
        self.min_chars = min_chars
        self.deictic = deictic

    # ── 1. 후보 쌍 ───────────────────────────────────────
    def candidates(self, audio: list[dict], visual: list[dict]) -> list[tuple[dict, dict, float]]:
        pairs = []
        for a in audio:
            for v in visual:
                r = overlap_ratio(a, v)
                if r >= self.overlap_min:
                    pairs.append((a, v, r))
        return pairs

    # ── 2. 문자열 병합 ───────────────────────────────────
    def merge(self, pairs: list[tuple[dict, dict, float]]) -> dict[str, str]:
        """visual claim_id → audio claim_id. 화면 Claim 하나는 ROUGE가 가장 높은 음성 Claim 하나에만 붙는다."""
        best: dict[str, tuple[float, float, str]] = {}
        for a, v, r in pairs:
            short = min(_norm(a["text"]), _norm(v["text"]), key=len)
            if len(short) < self.min_chars:
                continue
            score = rouge_l_recall(a["text"], v["text"])
            if score < self.rouge_min:
                continue
            if v["claim_id"] not in best or (score, r) > best[v["claim_id"]][:2]:
                best[v["claim_id"]] = (score, r, a["claim_id"])
        return {vid: aid for vid, (_, _, aid) in best.items()}

    # ── 3. Conflict (LLM) ────────────────────────────────
    def conflicts(self, pairs: list[tuple[dict, dict]]) -> list[tuple[str, str]]:
        if not pairs:
            return []
        out = parse_json_object(self.llm.chat(CONFLICT_SYSTEM, format_conflict_input(pairs)))
        found = []
        for c in out.get("conflicts", []):
            i = c.get("pair")
            if isinstance(i, int) and 0 <= i < len(pairs):
                found.append((pairs[i][0]["claim_id"], pairs[i][1]["claim_id"]))
        return found

    # ── 4. product / ingredient / brand (LLM) ───────────
    def product(self, audio: dict, visual: dict) -> dict:
        out = parse_json_object(self.llm.chat(PRODUCT_SYSTEM, format_product_input(audio, visual)))
        return {"product": out.get("product"), "ingredient": out.get("ingredient", []), "brand": out.get("brand")}

    # ── 5. target 규칙 ──────────────────────────────────
    def target(self, text: str, current, info: dict):
        t = _norm(text)
        names = [n for n in [info.get("product")] + list(info.get("ingredient") or []) if n]
        hits = [n for n in names if _norm(n) and _norm(n) in t]
        if hits:
            return info["product"] if info.get("product") in hits else max(hits, key=len)
        if info.get("product") and any(_norm(d) in t for d in self.deictic):
            return info["product"]
        return current

    # ── 전체 ────────────────────────────────────────────
    def align(self, audio: dict, visual: dict) -> dict:
        a_claims, v_claims = audio["claims"], visual["claims"]
        pairs = self.candidates(a_claims, v_claims)
        merged = self.merge(pairs)
        rest = [(a, v) for a, v, _ in pairs if merged.get(v["claim_id"]) != a["claim_id"]]
        conflict_pairs = self.conflicts(rest)
        info = self.product(audio, visual)
        print(f"  후보 쌍 {len(pairs)}, 병합 {len(merged)}, LLM 판정 쌍 {len(rest)}, conflict {len(conflict_pairs)}")
        return {**info, "claims": self.build(a_claims, v_claims, merged, conflict_pairs, info)}

    def build(self, a_claims: list[dict], v_claims: list[dict], merged: dict[str, str],
              conflict_pairs: list[tuple[str, str]], info: dict) -> list[AlignedClaim]:
        v_by = {c["claim_id"]: c for c in v_claims}
        rows: list[tuple[AlignedClaim, list[str]]] = []   # (claim, 이 행에 들어간 branch id들)
        for a in a_claims:
            vs = [v_by[vid] for vid, aid in merged.items() if aid == a["claim_id"]]
            rows.append((self._make([a], vs), [a["claim_id"]] + [v["claim_id"] for v in vs]))
        for v in v_claims:
            if v["claim_id"] not in merged:
                rows.append((self._make([], [v]), [v["claim_id"]]))

        order = sorted(range(len(rows)), key=lambda r: (rows[r][0].t_start, rows[r][0].t_end))
        branch_to_final = {}
        for n, r in enumerate(order):
            for bid in rows[r][1]:
                branch_to_final[bid] = f"c{n + 1:02d}"

        conflict_of: dict[str, str] = {}
        for aid, vid in conflict_pairs:
            ca, cv = branch_to_final[aid], branch_to_final[vid]
            if ca != cv:
                conflict_of.setdefault(ca, cv)
                conflict_of.setdefault(cv, ca)

        claims = []
        for r in order:
            claim, bids = rows[r]
            claim.claim_id = branch_to_final[bids[0]]
            claim.dup_of = branch_to_final.get(claim.dup_of) if claim.dup_of else None
            if claim.dup_of == claim.claim_id:
                claim.dup_of = None
            claim.conflict = conflict_of.get(claim.claim_id)
            claim.target = self.target(claim.text, claim.target, info)
            claims.append(claim)
        return claims

    @staticmethod
    def _make(a: list[dict], v: list[dict]) -> AlignedClaim:
        src = a + v
        base = src[0]
        types: list[str] = []
        for c in src:
            types += [t for t in c.get("types", []) if t not in types]
        t_start = min(c["t_start"] for c in src)
        t_end = max(c["t_end"] for c in src)
        return AlignedClaim(
            claim_id="",
            text=base["text"],
            t_start=t_start,
            t_end=t_end,
            duration=round(t_end - t_start, 3),
            target=base.get("target"),
            scope=base.get("scope"),
            speaker=base.get("speaker") if a else None,
            dup_of=base.get("dup_of"),       # branch id. build()에서 최종 id로 바꿈
            types=types,
            source="음성+화면" if a and v else ("음성" if a else "화면"),
            conflict=None,
            evidence={
                "audio": [{"claim_id": c["claim_id"], "segment_ids": c["segment_ids"]} for c in a],
                "visual": [{"claim_id": c["claim_id"], "frame_index": c["frame_index"],
                            "timestamp": c["timestamp"], "frame_path": c["frame_path"]} for c in v],
            },
        )
