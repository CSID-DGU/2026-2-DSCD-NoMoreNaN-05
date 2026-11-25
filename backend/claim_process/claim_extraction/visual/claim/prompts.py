from claim_process.prompt import load, render

from ...common import PROMPT_HEAD

TEXT_SYSTEM = render(load("visual_text_system", "PROMPT_HEAD"), PROMPT_HEAD=PROMPT_HEAD)
SPANS_USER = load("visual_text_user", "spans")
SCENE = load("visual_scene", "timestamp", "ocr_block", "cite_rules", "PROMPT_HEAD")
SCENE_OCR_HEAD = load("visual_scene_ocr_head")
SCENE_CITE = load("visual_scene_cite")


def format_spans(spans: list[dict]) -> str:
    lines = [f"[{s['span_id']}] {s['t_start']:.1f}~{s['t_end']:.1f}초: {s['text']}" for s in spans]
    return render(SPANS_USER, spans="\n".join(lines))


def format_scene(timestamp: float, spans: list[dict]) -> str:
    """spans: 이 프레임 시각에 걸친 글자 구간. 없으면 OCR 절·인용 규칙을 뺀다."""
    if not spans:
        ocr_block = cite_rules = ""
    else:
        ocr_block = "\n".join([SCENE_OCR_HEAD, *(f"({s['span_id']}) {s['text']}" for s in spans)]) + "\n"
        cite_rules = SCENE_CITE + "\n"
    return render(SCENE, timestamp=f"{timestamp:.1f}", ocr_block=ocr_block, cite_rules=cite_rules, PROMPT_HEAD=PROMPT_HEAD)
