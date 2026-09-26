from .schemas import Segment, Word

SENTENCE_END = (".", "?", "!", "。")


def segment_words(
    text: str,
    words: list[Word],
    pause_gap: float = 0.8,
    max_words: int = 40,
) -> list[Segment]:
    if not words:
        return [Segment(0, text, 0.0, 0.0)] if text else []

    slicer = _TextSlicer(text, words)
    segments: list[Segment] = []
    buf: list[int] = []

    for i, w in enumerate(words):
        buf.append(i)
        last = i == len(words) - 1
        gap = (words[i + 1].start - w.end) if not last else 0.0
        if (
            last
            or w.text.rstrip().endswith(SENTENCE_END)
            or gap >= pause_gap
            or len(buf) >= max_words
        ):
            segments.append(
                Segment(
                    id=len(segments),
                    text=slicer.slice(buf[0], buf[-1]),
                    start=words[buf[0]].start,
                    end=words[buf[-1]].end,
                )
            )
            buf = []
    return segments


class _TextSlicer:
    def __init__(self, text: str, words: list[Word]):
        self.text = text
        self.words = words
        self.ok = False

        orig_idx = [i for i, ch in enumerate(text) if not ch.isspace()]
        joined = "".join("".join(w.text.split()) for w in words)
        if len(joined) != len(orig_idx) or joined != "".join(text.split()):
            return

        self.ok = True
        self.spans: list[tuple[int, int]] = []
        pos = 0
        for w in words:
            n = len("".join(w.text.split()))
            self.spans.append((orig_idx[pos], orig_idx[pos + n - 1] + 1))
            pos += n

    def slice(self, first: int, last: int) -> str:
        if not self.ok:
            return " ".join(w.text for w in self.words[first : last + 1])
        return self.text[self.spans[first][0] : self.spans[last][1]].strip()
