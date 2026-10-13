from .schemas import Keyframe, Shot, TextSpan
from .video_io import VideoReader


def shot_candidates(
    reader: VideoReader, shots: list[Shot], interval: float, per_shot_max: int
) -> list[int]:
    out: list[int] = []
    for s in shots:
        length = s.end - s.start
        if length < 1.0:
            out.append(reader.time_to_index((s.start + s.end) / 2))
            continue
        t = s.start + interval / 2
        n = 0
        while t < s.end and n < per_shot_max:
            out.append(reader.time_to_index(t))
            t += interval
            n += 1
    return sorted(set(out))


def _shot_of(t: float, shots: list[Shot]) -> Shot:
    for s in shots:
        if s.start <= t < s.end:
            return s
    return shots[-1]


def aggregate(
    reader: VideoReader,
    shots: list[Shot],
    change: list[tuple[int, float]],
    texts: list[TextSpan],
    max_frames: int,
) -> list[Keyframe]:
    by_idx: dict[int, Keyframe] = {}

    for span in texts:
        t = reader.index_to_time(span.frame_index)
        s = _shot_of(t, shots)
        by_idx[span.frame_index] = Keyframe(
            frame_index=span.frame_index, timestamp=t, source="text",
            shot_id=s.id, shot_start=s.start, shot_end=s.end,
            text=span.text, text_start=span.start, text_end=span.end,
        )

    scores: dict[int, float] = {}
    for idx, dist in change:
        if idx in by_idx:
            continue
        t = reader.index_to_time(idx)
        s = _shot_of(t, shots)
        by_idx[idx] = Keyframe(
            frame_index=idx, timestamp=t, source="change",
            shot_id=s.id, shot_start=s.start, shot_end=s.end,
        )
        scores[idx] = dist

    frames = list(by_idx.values())
    if len(frames) > max_frames:
        drop = sorted(scores, key=scores.get)     # 변화 작은 순
        n_drop = len(frames) - max_frames
        dropped = set(drop[:n_drop])
        frames = [f for f in frames if f.frame_index not in dropped]

    return sorted(frames, key=lambda f: f.frame_index)
