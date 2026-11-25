"""audio·visual·alignment 공용. 두 conda env에서 모두 import하므로 표준 라이브러리만 쓴다."""
import json
import re
import unicodedata
import urllib.request
from collections import Counter
from decimal import Decimal

from claim_process.prompt import load, render

CLAIM_TYPES = ("EFFECT", "QUANTITY", "COMPOSITION", "CERTIFICATION", "PERSON_CREDENTIAL", "ETC")
CLAIM_FIELDS = ("text", "claim_type", "ingredients", "effect", "quantity", "intake_basis")

TYPE_RULES = load("common_claim_types")
PROMPT_HEAD = render(load("common_claim_head", "CLAIM_TYPES"), CLAIM_TYPES=TYPE_RULES)

_STRIP = re.compile(r"[\s.,!?~·'\"“”‘’()\[\]-]")
_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def norm(s: str) -> str:
    return _STRIP.sub("", s)


def kept(ch: str) -> bool:
    """aligner가 토큰에 남기는 글자 (qwen_asr Qwen3ForceAlignProcessor.is_kept_char와 같은 규칙)."""
    return ch == "'" or unicodedata.category(ch)[0] in "LN"


def keep(s: str) -> str:
    return "".join(ch for ch in s if kept(ch))


# ── 숫자·부정·정규형 (design §6). 모두 원문을 받는다. norm/keep은 . , 를 지워 1.5와 15를 같게 만든다 ──
_CMP = {"<": "미만", "≤": "이하", ">": "초과", "≥": "이상",
        "under": "미만", "below": "미만", "over": "초과", "above": "초과", "up to": "이하", "at least": "이상"}
_NUM = re.compile(
    r"(?:(<|>|≤|≥)\s*|\b(under|over|below|above|up to|at least)\s+)?"
    r"([-+±])?"
    r"(\d+(?:,\d{3})*(?:\.\d+)?)"
    r"(?:\s*(%|mg|g|kg|ml|l|μg|mcg|iu|cm|mm|kcal|명|주|일|개월|년|세|배|개|캡슐|정|포|위|등|억|만|천|회))?"
    r"(?:\s*(미만|이하|초과|이상))?",
    re.I)
_NEG_KO = ("없", "않", "못", "아니", "아닙", "불가", "금지")
_NEG_AN = re.compile(r"(?<!\S)안(?=\s)")
_NEG_EN = re.compile(r"\b(no|not|never|without)\b", re.I)
_NEG_NT = re.compile(r"n['’]t\b", re.I)


def _num_tokens(raw: str) -> list[tuple]:
    """[(sign, cmp, value, unit, 값 원문)], 원문 순서."""
    s = unicodedata.normalize("NFKC", raw).replace("−", "-")
    out = []
    for m in _NUM.finditer(s):
        front, word, sign, val, unit, back = m.groups()
        if sign and m.start() > 0 and s[m.start() - 1].isdigit():
            sign = None                                  # 40-75세: 범위 구분
        cmp = _CMP.get(front) or _CMP.get((word or "").lower()) or back
        digits = val.replace(",", "")
        out.append((sign, cmp, Decimal(digits), unit.lower() if unit else None, digits))
    return out


def numbers(raw: str) -> list[tuple]:
    """[(sign, cmp, value, unit)], 원문 순서."""
    return [t[:4] for t in _num_tokens(raw)]


def num_compatible(a: str, b: str) -> bool:
    na = sorted(numbers(a), key=lambda t: t[2])
    nb = sorted(numbers(b), key=lambda t: t[2])
    if len(na) != len(nb):
        return False
    for (sa, ca, va, ua), (sb, cb, vb, ub) in zip(na, nb):
        if va != vb or ca != cb:
            return False
        if ua and ub and ua != ub:
            return False
        if sa and sb and sa != sb:
            return False
    return True


def num_prefix(short: str, long: str) -> bool:
    """OCR 타이핑 중간 프레임: short가 long의 앞부분."""
    if not keep(long).startswith(keep(short)):
        return False
    ns, nl = _num_tokens(short), _num_tokens(long)
    if len(ns) > len(nl):
        return False
    for i, (s, l) in enumerate(zip(ns, nl)):
        if s[:4] == l[:4]:
            continue
        if i == len(ns) - 1 and short.strip()[-1:].isdigit() and s[0] == l[0] and s[1] == l[1] \
                and l[4].startswith(s[4]):
            continue
        return False
    return True


def neg_profile(raw: str) -> Counter:
    c = Counter()
    for w in _NEG_KO:
        if raw.count(w):
            c[w] = raw.count(w)
    if n := len(_NEG_AN.findall(raw)):
        c["안"] = n
    for w in _NEG_EN.findall(raw):
        c[w.lower()] += 1
    if n := len(_NEG_NT.findall(raw)):
        c["n't"] = n
    return c


def merge_safe(a: str, b: str) -> bool:
    """필요조건 필터일 뿐 동치 보장 아님."""
    return num_compatible(a, b) and neg_profile(a) == neg_profile(b)


def canon_equal(a: str, b: str) -> bool:
    """띄어쓰기·문장부호·전각·대소문자 차이만 허용."""
    ka = keep(unicodedata.normalize("NFKC", a)).lower()
    kb = keep(unicodedata.normalize("NFKC", b)).lower()
    return ka == kb and numbers(a) == numbers(b) and neg_profile(a) == neg_profile(b)


same_text = canon_equal


def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def similarity(a: str, b: str) -> float:
    """1 − 편집거리 / 긴 쪽 길이."""
    if not a and not b:
        return 1.0
    return 1.0 - levenshtein(a, b) / max(len(a), len(b))


def clean_types(value) -> list[str]:
    """문자열·배열 → 6종 안의 중복 없는 배열(순서 유지). 무효면 []."""
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(t for t in value if isinstance(t, str) and t in CLAIM_TYPES))


def check_items(items: list[dict], where: str) -> list[dict]:
    """claim_type을 배열로 맞춘다. 6종 밖 원소는 로그 후 빼고 남는 것이 없으면 제외, ingredients가 null이면 []."""
    out = []
    for it in items:
        raw = it.get("claim_type")
        types = clean_types(raw)
        if not types:
            print(f"  [drop] {where}: claim_type={raw!r} {it.get('text')}")
            continue
        if isinstance(raw, list) and (bad := [t for t in raw if t not in types]):
            print(f"  [warn] {where}: claim_type {bad!r} 제외 {it.get('text')}")
        it["claim_type"] = types
        if it.get("ingredients") is None:
            it["ingredients"] = []
        out.append(it)
    return out


class LLMClient:
    """llama-server(OpenAI 호환 API)로 띄운 gpt-oss를 부른다. serve_llm.sh 참고."""

    def __init__(self, base_url: str, model: str, temperature: float = 0.0, reasoning_effort: str = "low",
                 max_tokens: int | None = None, timeout: float | None = None):
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.model = model
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort
        self.max_tokens = max_tokens
        self.timeout = timeout

    def chat(self, system: str, user: str, schema: dict | None = None) -> str:
        """schema가 있으면 response_format json_schema. llama.cpp gpt-oss 파서는 final 채널만 문법으로 제약한다."""
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": self.temperature,
            "reasoning_effort": self.reasoning_effort,
        }
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "output", "schema": schema}}
        if self.max_tokens is not None:
            body["max_tokens"] = self.max_tokens
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with (urllib.request.urlopen(req) if self.timeout is None
              else urllib.request.urlopen(req, timeout=self.timeout)) as r:
            out = json.load(r)
        t = out.get("timings", {})
        if t:
            print(f"    {t.get('prompt_n', 0)} prompt tok @ {t.get('prompt_per_second', 0):.0f}/s, "
                  f"{t.get('predicted_n', 0)} gen tok @ {t.get('predicted_per_second', 0):.1f}/s", flush=True)
        return out["choices"][0]["message"]["content"] or ""


def parse_json_array(text: str) -> list:
    text = _FENCE.sub("", text.strip())
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"JSON 배열을 찾지 못함:\n{text}")
    return json.loads(text[start : end + 1])


def parse_json_object(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"JSON 객체를 찾지 못함:\n{text}")
    return json.loads(text[start : end + 1])
