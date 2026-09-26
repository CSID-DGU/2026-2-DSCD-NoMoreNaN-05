from .llm import LLMClient, parse_json_array
from .prompts import SYSTEM, format_segments
from .schemas import CLAIM_TYPES, Claim
from stt.schemas import Segment


class ClaimExtractor:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def extract(self, segments: list[Segment]) -> list[Claim]:
        if not segments:
            return []
        raw = self.llm.chat(SYSTEM, format_segments(segments))
        by_id = {s.id: s for s in segments}

        claims = []
        for item in parse_json_array(raw):
            segs = [by_id[i] for i in item.get("segment_ids", []) if i in by_id]
            if not item.get("claim") or not segs:
                print(f"  [skip] 근거 세그먼트 없음: {item}")
                continue
            start = min(s.start for s in segs)
            end = max(s.end for s in segs)
            claims.append(
                Claim(
                    claim=item["claim"].strip(),
                    types=[t for t in item.get("types", []) if t in CLAIM_TYPES],
                    source="음성",
                    start=start,
                    end=end,
                    duration=round(end - start, 3),
                    segment_ids=[s.id for s in segs],
                    quote=item.get("quote", "").strip(),
                )
            )
        return claims
