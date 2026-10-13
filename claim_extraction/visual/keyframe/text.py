import re

import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

from .schemas import TextSpan
from .video_io import VideoReader

_WS = re.compile(r"\s+")


def _norm(s: str) -> str:
    return _WS.sub("", s).strip()


class TextDetector:
    def __init__(self, model: str, device: str = "cuda:0", max_new_tokens: int = 512):
        self.device = device
        self.processor = AutoProcessor.from_pretrained(model)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model, dtype=torch.bfloat16
        ).to(device).eval()
        self.max_new_tokens = max_new_tokens

    @torch.no_grad()
    def ocr(self, image: Image.Image) -> str:
        messages = [{"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": "OCR:"},
        ]}]
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt",
        ).to(self.device)
        out = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False)
        return self.processor.decode(out[0][inputs["input_ids"].shape[-1]:-1]).strip()

    def scan(self, reader: VideoReader, interval: float, min_chars: int = 2) -> list[TextSpan]:
        step = max(1, int(round(interval * reader.fps)))
        spans: list[TextSpan] = []

        group_start = None      # 현재 문구 그룹의 첫 프레임
        longest = ""            # 그룹에서 가장 긴 텍스트
        longest_frame = None    # longest가 처음 나온 프레임
        last_frame = None

        def close():
            if group_start is not None and len(_norm(longest)) >= min_chars:
                spans.append(TextSpan(
                    text=longest,
                    start=reader.index_to_time(group_start),
                    end=reader.index_to_time(min(last_frame + step, reader.n_frames - 1)),
                    frame_index=longest_frame,
                ))

        for idx in range(0, reader.n_frames, step):
            text = self.ocr(reader.frame(idx))
            n = _norm(text)
            if not n:
                close()
                group_start = None
                longest = ""
                continue

            if group_start is None:
                group_start, longest, longest_frame = idx, text, idx
            elif n in _norm(longest):            
                pass
            elif _norm(longest) in n:           
                longest, longest_frame = text, idx
            else:                             
                close()
                group_start, longest, longest_frame = idx, text, idx
            last_frame = idx

        close()
        return spans
