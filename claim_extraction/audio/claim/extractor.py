from .llm import LLMClient, parse_json_array
from .prompts import SYSTEM, format_segments
from .schemas import Claim
from ..stt.schemas import Segment

class ClaimExtractor:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def extract(self, segments: list[Segment]) -> list[Claim]:
        if not segments:
            return []
        raw = self.llm.chat(SYSTEM, format_segments(segments))
        return self.build(parse_json_array(raw), segments)

    @staticmethod
    def build(items: list[dict], segments: list[Segment]) -> list[Claim]:
        by_id = {s.id: s for s in segments}
        claims: list[Claim] = []
        index_to_id: dict[int, str] = {}   # LLM 배열 인덱스 → claim_id (dup_of 변환용)

        for i, item in enumerate(items):
            text = (item.get("text") or "").strip()
            segs = [by_id[j] for j in item.get("segment_ids", []) if j in by_id]
            if not text or not segs:
                print(f"  [skip] 근거 세그먼트 없음: {item}")
                continue
            claim_id = f"a{len(claims) + 1:02d}"
            dup = item.get("dup_of")
            dup_of = index_to_id.get(dup) if isinstance(dup, int) else None
            index_to_id[i] = claim_id
            t_start = min(s.start for s in segs)
            t_end = max(s.end for s in segs)
            claims.append(
                Claim(
                    claim_id=claim_id,
                    text=text,
                    t_start=t_start,
                    t_end=t_end,
                    duration=round(t_end - t_start, 3),
                    target=(item.get("target") or None),
                    scope=item.get("scope"),
                    speaker=item.get("speaker"),
                    dup_of=dup_of,
                    types=item.get("types", []),
                    source="음성",
                    segment_ids=[s.id for s in segs],
                )
            )
        return claims
