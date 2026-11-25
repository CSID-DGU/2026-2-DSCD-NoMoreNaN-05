from PIL import Image

from ...common import CLAIM_FIELDS, check_items, norm, parse_json_array, same_text
from .prompts import format_scene
from .vlm import VLM


class SceneClaimExtractor:
    """선택 프레임을 한 장씩, 그 시각에 걸친 OCR 글자 줄과 함께 VLM에 넣는다. 글자 Claim과 시각 Claim을 함께 낸다.
    시각: 인용한 OCR 줄(span_ids)이 있으면 그 글자 구간, 없으면 이 프레임 ~ 다음 선택 프레임."""

    def __init__(self, vlm: VLM):
        self.vlm = vlm

    def extract(self, frames: list[dict], duration: float, spans: list[dict]) -> list[dict]:
        by_id = {s["span_id"]: s for s in spans}
        claims = []
        for i, f in enumerate(frames):
            frame_end = frames[i + 1]["timestamp"] if i + 1 < len(frames) else duration
            shown = [s for s in spans
                     if s["t_start"] <= f["timestamp"] < s["t_end"] or s["frame_index"] == f["frame_index"]]
            raw = self.vlm.ask(Image.open(f["path"]).convert("RGB"), format_scene(f["timestamp"], shown))
            try:
                items = parse_json_array(raw)
            except ValueError as e:
                print(f"  [skip] frame #{f['frame_index']}: {e}")
                continue
            for it in check_items(items, f"scene #{f['frame_index']}"):
                text = (it.get("text") or "").strip()
                if not norm(text):
                    continue
                if any(same_text(text, c["text"]) for c in claims):
                    print(f"  [dup] frame #{f['frame_index']}: {text}")
                    continue
                used = [by_id[j] for j in it.get("span_ids") or [] if j in by_id]
                claims.append({
                    "claim_id": f"s{len(claims) + 1:02d}",
                    **{k: it.get(k) for k in CLAIM_FIELDS},
                    "text": text,
                    "t_start": min(s["t_start"] for s in used) if used else f["timestamp"],
                    "t_end": max(s["t_end"] for s in used) if used else frame_end,
                    "span_ids": [s["span_id"] for s in used],
                    "frame_index": f["frame_index"],
                    "frame_path": f["path"],
                })
        return claims
