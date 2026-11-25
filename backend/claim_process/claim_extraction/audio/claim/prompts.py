from claim_process.prompt import load, render

from ...common import PROMPT_HEAD
from ..stt.schemas import Segment

SYSTEM = render(load("audio_claim_system", "PROMPT_HEAD"), PROMPT_HEAD=PROMPT_HEAD)
SEGMENTS_USER = load("audio_claim_user", "segments")


def format_segments(segments: list[Segment]) -> str:
    lines = [f"[{s.id}] {s.start:.1f}~{s.end:.1f}초: {s.text}" for s in segments]
    return render(SEGMENTS_USER, segments="\n".join(lines))
