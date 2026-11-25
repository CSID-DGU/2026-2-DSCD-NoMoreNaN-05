from claim_process.prompt import load, render

from ..common import CLAIM_TYPES, TYPE_RULES, canon_equal, keep

REPEAT_MIN = 2             # 반복 노출 줄: 같은 정규형 줄이 이 구간 수 이상

JUDGE_SYSTEM = load("alignment_judge_system")
JUDGE_USER = load("alignment_judge_user", "pairs")
TYPES_SYSTEM = render(load("alignment_types_system", "CLAIM_TYPES"), CLAIM_TYPES=TYPE_RULES)
TYPES_USER = load("alignment_types_user", "claims")
PRODUCTS_SYSTEM = load("alignment_products_system")
PRODUCTS_TITLE_RULES = load("alignment_products_title_system")
PRODUCTS_USER = load("alignment_products_user", "audio", "screens", "repeats", "scene", "claims")
PRODUCTS_TITLE_USER = load("alignment_products_title_user", "title")

_NAME = {"type": ["string", "null"]}
_IDS = {"type": "array", "items": {"type": "integer"}}
PRODUCTS_SCHEMA = {
    "type": "object",
    "properties": {
        "products": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "product_ref": _NAME, "product_name": _NAME, "brand_name": _NAME,
                "manufacturer_name": _NAME, "manufacturing_report_number": _NAME,
                "evidence": {"type": "object", "properties": {"product_name": _IDS, "brand_name": _IDS},
                             "required": ["product_name", "brand_name"]},
            },
            "required": ["product_ref", "product_name", "brand_name", "manufacturer_name",
                         "manufacturing_report_number", "evidence"],
        }},
        "claim_products": {"type": "object", "additionalProperties": _NAME},
    },
    "required": ["products", "claim_products"],
}


def judge_schema(n: int) -> dict:
    """판정 묶음 n쌍용. 구조만 보장하며 번호 누락·중복은 앱에서 검사한다."""
    return {
        "type": "object",
        "properties": {"verdicts": {
            "type": "array", "minItems": n, "maxItems": n,
            "items": {"type": "object",
                      "properties": {"pair": {"type": "integer", "minimum": 0, "maximum": n - 1},
                                     "verdict": {"type": "string", "enum": ["SAME", "CONFLICT", "UNRELATED"]}},
                      "required": ["pair", "verdict"]},
        }},
        "required": ["verdicts"],
    }


def types_schema(n: int) -> dict:
    """유형 묶음 n건용. judge_schema와 같은 꼴."""
    return {
        "type": "object",
        "properties": {"types": {
            "type": "array", "minItems": n, "maxItems": n,
            "items": {"type": "object",
                      "properties": {"claim": {"type": "integer", "minimum": 0, "maximum": n - 1},
                                     "claim_type": {"type": "array", "minItems": 1, "maxItems": len(CLAIM_TYPES),
                                                    "items": {"type": "string", "enum": list(CLAIM_TYPES)}}},
                      "required": ["claim", "claim_type"]},
        }},
        "required": ["types"],
    }


def format_types_input(texts: list[str]) -> str:
    return render(TYPES_USER, claims="\n".join(f"[{i}] {t}" for i, t in enumerate(texts)))


def _t(c: dict) -> str:
    return f"{c['t_start']:.1f}~{c['t_end']:.1f}초"


def format_judge_input(pairs: list[tuple[str, str, dict, str, dict]]) -> str:
    """pairs: (time|global, A 브랜치, A, B 브랜치, B)"""
    lines = [f"[{i}] ({kind}) A({ab}, {_t(a)}): {a['text']} / B({bb}, {_t(b)}): {b['text']}"
             for i, (kind, ab, a, bb, b) in enumerate(pairs)]
    return render(JUDGE_USER, pairs="\n".join(lines))


def shown_from(s: dict) -> float:
    """대표 표기가 보이기 시작한 시각. t_rep 없는 이전 형식 파일은 t_start."""
    return s.get("t_rep", s["t_start"])


def format_screens(texts: list[dict]) -> list[str]:
    """새 줄이 나타난 시각 T마다 t_rep ≤ T < t_end인 줄 전부(span_id 순)를 한 화면으로."""
    return [f"[{T:.1f}초 화면] " + " | ".join(f"({s['span_id']}) {s['text']}" for s in texts if shown_from(s) <= T < s["t_end"])
            for T in sorted({shown_from(s) for s in texts})]


def format_repeats(texts: list[dict]) -> list[str]:
    """정규형이 같은 줄을 묶어 REPEAT_MIN 구간 이상인 것만, 구간 수 내림차순. 숫자만인 줄(전화번호 등) 제외.
    대표 표기 = 가장 많이 나온 원문, 동률이면 짧은 것."""
    groups: list[list[dict]] = []
    for s in texts:
        k = keep(s["text"])
        if not k or k.isdigit():
            continue
        g = next((g for g in groups if canon_equal(g[0]["text"], s["text"])), None)
        if g is None:
            groups.append([s])
        else:
            g.append(s)
    rows = []
    for g in sorted((g for g in groups if len(g) >= REPEAT_MIN), key=len, reverse=True):
        names = [s["text"] for s in g]
        rep = min(names, key=lambda t: (-names.count(t), len(t)))
        rows.append(f"{rep} ×{len(g)} (" + ", ".join(f"{shown_from(s):.1f}" for s in g) + "초) ["
                    + ", ".join(str(s["span_id"]) for s in g) + "]")
    return rows


def screens(data: dict) -> list[dict]:
    """OCR 글자 구간. text 브랜치 파일에 있으면 그것, 없으면 scene 파일의 것."""
    if "text" in data:
        return data["text"]["screen_texts"]
    return data["scene"].get("screen_texts", []) if "scene" in data else []


def format_products_input(data: dict, claims: list[tuple[str, str]], title: str | None = None) -> str:
    """data: 브랜치 → 브랜치 파일 내용, claims: [(claim_id, text)]. 꺼진 브랜치 절은 (없음). title이 있으면 맨 앞에 제목 절."""
    audio = data["audio"]["transcript"] if "audio" in data else []
    texts = screens(data)
    scene = data["scene"]["claims"] if "scene" in data else []

    def rows(xs: list[str]) -> str:
        return "\n".join(xs) or "(없음)"

    body = render(PRODUCTS_USER,
                  audio=rows([f"{_t(s)}: {s['text']}" for s in audio]),
                  screens=rows(format_screens(texts)),
                  repeats=rows(format_repeats(texts)),
                  scene=rows([f"{_t(c)}: {c['text']}" for c in scene]),
                  claims=rows([f"[{cid}] {text}" for cid, text in claims])).strip()
    return (render(PRODUCTS_TITLE_USER, title=title) if title else "") + body
