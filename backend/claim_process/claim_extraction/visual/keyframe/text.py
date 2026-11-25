from collections import Counter

import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

from claim_process.prompt import load

from ...common import merge_safe, neg_profile, norm, num_compatible, num_prefix, similarity
from .schemas import Frame, TextSpan
from .video_io import VideoReader

OCR_TASK = load("visual_ocr_task")


def _rep(g: dict) -> str:
    """등장 횟수 최다, 동률이면 더 긴 변형."""
    return max(g["variants"], key=lambda v: (g["variants"][v], len(v)))


def rep_frames(spans: list[TextSpan]) -> list[Frame]:
    """글자 구간마다 대표 표기가 처음 읽힌 프레임(frame_index). 같은 프레임은 하나로. 완성 화면이라는 보장은 없다."""
    first = {}
    for s in spans:
        first.setdefault(s.frame_index, s.t_rep)
    return [Frame(idx, t, None, source="text") for idx, t in sorted(first.items())]


def cyrillic_line(line: str) -> bool:
    """한글이 없고 글자 중 키릴 문자가 절반 이상인 줄(거울상 오인식)."""
    letters = [ch for ch in line if ch.isalpha()]
    if not letters or any("가" <= ch <= "힣" for ch in line):
        return False
    return sum("\u0400" <= ch <= "\u04ff" for ch in letters) / len(letters) >= 0.5


def same_line(n: str, r: str, sim_min: float) -> tuple[bool, float]:
    """n: 이 줄 원문, r: 그룹 대표 변형 원문. 유사도는 norm 문자열로, 숫자·부정은 원문으로."""
    a, b = norm(n), norm(r)
    sim = similarity(a, b)
    if sim >= sim_min and merge_safe(n, r):
        return True, sim
    if a in b or b in a:
        short, long = (n, r) if len(a) <= len(b) else (r, n)
        if neg_profile(n) == neg_profile(r) and (num_compatible(short, long) or num_prefix(short, long)):
            return True, sim
    return False, sim


class TextDetector:
    def __init__(self, model: str, device: str = "cuda:0", max_new_tokens: int = 512,
                 batch: int = 1, max_pixels: int = 1280 * 28 * 28):
        self.device = device
        self.processor = AutoProcessor.from_pretrained(model)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model, dtype=torch.bfloat16
        ).to(device).eval()
        self.max_new_tokens = max_new_tokens
        self.batch = batch
        self.size = {"shortest_edge": self.processor.image_processor.size.shortest_edge, "longest_edge": max_pixels}

    @torch.no_grad()
    def ocr_batch(self, images: list[Image.Image]) -> list[str]:
        messages = [[{"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": OCR_TASK},
        ]}] for image in images]
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt",
            processor_kwargs={"padding": True, "padding_side": "left", "images_kwargs": {"size": self.size}},
        ).to(self.device)
        # 모델 generation_config가 use_cache: false라 토큰마다 이미지 포함 전체를 재계산함 → 켬 (사용자 결정 10-26)
        out = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False, use_cache=True)
        n = inputs["input_ids"].shape[-1]
        return [t.strip() for t in self.processor.batch_decode(out[:, n:], skip_special_tokens=True)]

    def scan(self, reader: VideoReader, interval: float, sim_min: float, min_chars: int = 2) -> list[TextSpan]:
        """OCR 결과를 줄 단위로, 연속 프레임에서 편집거리 유사도·포함 관계로 이어지는 줄을 한 구간으로 묶는다.
        한 프레임만 OCR에서 빠진 줄은 이어 붙이고, 연속 2프레임 빠지면 구간을 닫는다."""
        step = max(1, int(round(interval * reader.fps)))
        spans: list[TextSpan] = []
        groups: list[dict] = []        # 열린 그룹

        def close(g: dict):
            rep = _rep(g)
            spans.append(TextSpan(
                text=rep,
                start=reader.index_to_time(g["first"]),
                end=reader.index_to_time(min(g["last"] + step, reader.n_frames - 1)),
                t_rep=reader.index_to_time(g["first_of"][rep]),
                frame_index=g["first_of"][rep],
            ))

        indices = list(range(0, reader.n_frames, step))
        texts = []
        for k in range(0, len(indices), self.batch):
            texts += self.ocr_batch([reader.frame(i) for i in indices[k:k + self.batch]])

        for idx, text in zip(indices, texts):
            lines = [l.strip() for l in text.split("\n")]
            lines = [l for l in lines if len(norm(l)) >= min_chars and not cyrillic_line(l)]
            lines = list(dict.fromkeys(lines))      # 같은 프레임의 반복 줄은 하나로
            matched: list[dict] = []
            for line in lines:
                best, best_sim = None, -1.0
                for g in groups:
                    if any(g is m for m in matched):
                        continue
                    ok, sim = same_line(line, _rep(g), sim_min)
                    if ok and sim > best_sim:
                        best, best_sim = g, sim
                if best is None:
                    best = {"variants": Counter(), "first": idx, "last": idx, "first_of": {}, "miss": 0}
                    groups.append(best)
                best["variants"][line] += 1
                best["last"] = idx
                best["miss"] = 0
                best["first_of"].setdefault(line, idx)
                matched.append(best)
            still_open = []
            for g in groups:
                if any(g is m for m in matched):
                    continue
                g["miss"] += 1
                if g["miss"] >= 2:
                    close(g)
                else:
                    still_open.append(g)
            groups = matched + still_open

        for g in groups:
            close(g)
        return sorted(spans, key=lambda s: (s.start, s.frame_index))
