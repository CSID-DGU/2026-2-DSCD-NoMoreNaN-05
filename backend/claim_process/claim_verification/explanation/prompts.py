import json

from claim_process.prompt import load, render

SENTENCE_CHARS = 60

SYSTEM = render(load("explanation_system", "SENTENCE_CHARS"), SENTENCE_CHARS=str(SENTENCE_CHARS))
RECORD_USER = load("explanation_user", "record")
POPUP_SYSTEM = load("popup_summary_system")
POPUP_USER = load("popup_summary_user", "template", "record")
POPUP_TEMPLATES = {case: load(f"popup_summary_{case}") for case in ("violation", "overclaim", "both", "none")}
POPUP_SCHEMA = {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]}


def format_user(payload: dict) -> str:
    return render(RECORD_USER, record=json.dumps(payload, ensure_ascii=False, indent=1))


def explain_schema(n: int, has_b: bool) -> dict:
    return {"type": "object",
            "properties": {"claim": {"type": "string"},
                           "checks": {"type": "array", "minItems": n, "maxItems": n, "items": {"type": "string"}},
                           "B": {"type": "string"} if has_b else {"type": "null"}},
            "required": ["claim", "checks", "B"]}


def format_popup(case: str, payload: dict) -> str:
    return render(POPUP_USER, template=POPUP_TEMPLATES[case], record=json.dumps(payload, ensure_ascii=False, indent=1))
