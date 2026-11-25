import re

from ...common import keep, kept
from .schemas import Segment, Word

_SENTENCE = re.compile(r".*?[.?!]+\s*|.+$", re.S)


class CharTimeline:
    """본문에서 aligner가 남기는 글자마다 aligner 토큰 시간을 붙인다."""

    def __init__(self, text: str, words: list[Word]):
        self.text = text
        self.pos = [i for i, ch in enumerate(text) if kept(ch)]      # k번째 글자의 본문 위치
        body = "".join(text[i] for i in self.pos)
        joined = "".join(keep(w.text) for w in words)
        if joined != body:
            raise ValueError(f"본문과 aligner 토큰의 글자가 다름\n본문: {body}\n토큰: {joined}")
        self.times = [(w.start, w.end) for w in words for _ in keep(w.text)]   # k번째 글자의 (start, end)

    def time_of(self, pos_start: int, pos_end: int) -> tuple[float, float]:
        ks = [k for k, i in enumerate(self.pos) if pos_start <= i < pos_end]
        return self.times[ks[0]][0], self.times[ks[-1]][1]


def split_sentences(tl: CharTimeline) -> list[Segment]:
    """본문을 . ? ! 뒤에서 자른다."""
    segments = []
    for m in _SENTENCE.finditer(tl.text):
        if not keep(m.group()):
            continue
        start, end = tl.time_of(m.start(), m.end())
        segments.append(Segment(len(segments), m.group().strip(), start, end, m.start(), m.end()))
    return segments
