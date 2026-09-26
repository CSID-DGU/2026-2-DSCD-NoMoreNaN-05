from pathlib import Path

import torch
from qwen_asr import Qwen3ASRModel

from .schemas import Word


class Transcriber:
    def __init__(self, model: str, aligner: str, device: str = "cuda:0"):
        self.model = Qwen3ASRModel.from_pretrained(
            model,
            dtype=torch.bfloat16,
            device_map=device,
            forced_aligner=aligner,
            forced_aligner_kwargs=dict(dtype=torch.bfloat16, device_map=device),
        )

    def transcribe(self, wav: Path, language: str = "Korean") -> tuple[str, list[Word]]:
        result = self.model.transcribe(
            audio=str(wav), language=language, return_time_stamps=True
        )[0]
        words = [
            Word(t.text, float(t.start_time), float(t.end_time))
            for t in (result.time_stamps or [])
        ]
        return result.text, words
