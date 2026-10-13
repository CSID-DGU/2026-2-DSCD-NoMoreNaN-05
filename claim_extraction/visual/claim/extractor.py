import re

from PIL import Image

from ..keyframe import Keyframe

from .prompts import format_prompt
from .schemas import VisualClaim
from .vlm import VLM, parse_json_array

_STRIP = re.compile(r"[\s.,!?~·'\"“”‘’()\[\]-]")


def _norm(s: str) -> str:
    return _STRIP.sub("", s)


class VisualClaimExtractor:
    def __init__(self, vlm: VLM):
        self.vlm = vlm

    def extract(self, keyframes: list[Keyframe]) -> list[VisualClaim]:
        claims: list[VisualClaim] = []
        for kf in keyframes:
            raw = self.vlm.ask(Image.open(kf.path).convert("RGB"), format_prompt(kf))
            try:
                items = parse_json_array(raw)
            except ValueError as e:
                print(f"  [skip] frame #{kf.frame_index}: {e}")
                continue
            claims.extend(self.build(items, kf, len(claims)))
        return self.mark_dups(claims)

    @staticmethod
    def build(items: list[dict], kf: Keyframe, offset: int = 0) -> list[VisualClaim]:
        # 글자에서 나온 프레임이면 글자 노출 구간, 아니면 샷 구간
        if kf.source == "text":
            t_start, t_end = kf.text_start, kf.text_end
        else:
            t_start, t_end = kf.shot_start, kf.shot_end

        claims = []
        for it in items:
            text = (it.get("text") or "").strip()
            if not text:
                continue
            claims.append(VisualClaim(
                claim_id=f"v{offset + len(claims) + 1:02d}",
                text=text,
                t_start=t_start,
                t_end=t_end,
                duration=round(t_end - t_start, 3),
                target=(it.get("target") or None),
                scope=it.get("scope"),
                speaker=None,
                dup_of=None,
                types=it.get("types", []),
                source="화면",
                timestamp=kf.timestamp,
                frame_index=kf.frame_index,
                frame_path=kf.path,
            ))
        return claims

    @staticmethod
    def mark_dups(claims: list[VisualClaim]) -> list[VisualClaim]:
        # 같은 글자가 여러 프레임에서 뽑히면 뒤의 것에 최초 claim_id를 적는다
        first: dict[str, str] = {}
        for c in claims:
            key = _norm(c.text)
            if key in first:
                c.dup_of = first[key]
            else:
                first[key] = c.claim_id
        return claims
