from ...common import CLAIM_FIELDS, LLMClient, check_items, norm, parse_json_array, same_text
from .prompts import TEXT_SYSTEM, format_spans


class TextClaimExtractor:
    """화면 글자 구간 목록 전체를 gpt-oss에 한 번에 넣는다."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def extract(self, spans: list[dict]) -> list[dict]:
        if not spans:
            return []
        raw = self.llm.chat(TEXT_SYSTEM, format_spans(spans))
        try:
            items = parse_json_array(raw)
        except ValueError as e:
            print(f"  [skip] text: {e}")
            return []
        return self.build(items, spans)

    @staticmethod
    def build(items: list[dict], spans: list[dict]) -> list[dict]:
        by_id = {s["span_id"]: s for s in spans}
        rows = []
        for it in check_items(items, "text"):
            text = (it.get("text") or "").strip()
            used = [by_id[j] for j in it.get("span_ids") or [] if j in by_id]
            if not norm(text) or not used:
                print(f"  [skip] 근거 글자 구간 없음: {it}")
                continue
            rows.append({
                **{f: it.get(f) for f in CLAIM_FIELDS},
                "text": text,
                "t_start": min(s["t_start"] for s in used),
                "t_end": max(s["t_end"] for s in used),
                "span_ids": [s["span_id"] for s in used],
            })
        rows.sort(key=lambda r: (r["t_start"], r["t_end"]))
        kept = []
        for r in rows:
            if any(same_text(r["text"], k["text"]) for k in kept):
                print(f"  [dup] text: {r['text']}")
                continue
            kept.append(r)
        return [{"claim_id": f"t{i + 1:02d}", **r} for i, r in enumerate(kept)]
