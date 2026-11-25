from ...common import CLAIM_FIELDS, LLMClient, check_items, keep, parse_json_array, same_text
from ..stt.schemas import Segment
from ..stt.segmenter import CharTimeline
from .prompts import SYSTEM, format_segments


class ClaimExtractor:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def extract(self, segments: list[Segment], tl: CharTimeline) -> list[dict]:
        if not segments:
            return []
        raw = self.llm.chat(SYSTEM, format_segments(segments))
        try:
            items = parse_json_array(raw)
        except ValueError as e:
            print(f"  [skip] audio: {e}")
            return []
        return self.build(items, segments, tl)

    @staticmethod
    def build(items: list[dict], segments: list[Segment], tl: CharTimeline) -> list[dict]:
        """본문에서 text 위치를 찾으면 글자 시간·위치로 segment_ids를 정한다. 못 찾으면 LLM의 segment_ids."""
        by_id = {s.id: s for s in segments}
        body = keep(tl.text)
        claims = []
        for it in check_items(items, "audio"):
            text = (it.get("text") or "").strip()
            key = keep(text)
            if not key:
                print(f"  [skip] 빈 text: {it}")
                continue
            if any(same_text(text, c["text"]) for c in claims):
                print(f"  [dup] audio: {text}")
                continue
            k = body.find(key)
            if k >= 0:
                t_start, t_end = tl.times[k][0], tl.times[k + len(key) - 1][1]
                p0, p1 = tl.pos[k], tl.pos[k + len(key) - 1] + 1
                segs = [s for s in segments if s.char_start < p1 and s.char_end > p0]
            else:
                segs = [by_id[j] for j in it.get("segment_ids") or [] if j in by_id]
                if not segs:
                    print(f"  [skip] 본문에 없고 근거 세그먼트 없음: {it}")
                    continue
                print(f"  [warn] 본문에 없음 → 세그먼트 시간 사용: {text}")
                t_start, t_end = min(s.start for s in segs), max(s.end for s in segs)
            claims.append({
                "claim_id": f"a{len(claims) + 1:02d}",
                **{f: it.get(f) for f in CLAIM_FIELDS},
                "text": text,
                "t_start": t_start,
                "t_end": t_end,
                "segment_ids": [s.id for s in segs],
            })
        return claims
