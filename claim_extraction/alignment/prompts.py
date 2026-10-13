import json

PRODUCT_SYSTEM = """너는 건강기능식품 SNS 광고의 음성 대본과 화면 글자를 보고, 이 영상이 광고하는 제품명·원료명·브랜드명을 찾는다.

## 규칙
- 대본이나 화면 글자에 실제로 나온 표기만 적는다. 추측하거나 보태지 않는다.
- product: 광고하는 제품명 하나. 없으면 null.
- ingredient: 광고에서 언급한 기능성 원료·성분명 목록. 없으면 [].
- brand: 브랜드·회사명. 없으면 null.

## 출력
JSON 객체만 출력한다. 다른 설명은 쓰지 않는다.
{"product": "혈행톡", "ingredient": ["베르베린", "플라보노이드"], "brand": null}"""

CONFLICT_SYSTEM = """너는 건강기능식품 SNS 광고에서 같은 시각에 나온 음성 Claim과 화면 글자의 쌍을 보고, 둘의 내용이 서로 어긋나는지 판정한다.

## 어긋남(conflict)의 뜻
음성이 주장하는 것을 화면 글자가 부정·제한·조건부로 만드는 경우.
예) 음성 "확실한 효과가 있습니다" + 화면 "개인차가 있을 수 있습니다" → conflict
예) 음성 "2주면 변화를 느낍니다" + 화면 "개인에 따라 효과가 다를 수 있음" → conflict
예) 음성 "혈당을 42% 낮춥니다" + 화면 "-42%" → 같은 내용, conflict 아님
예) 음성 "혈당을 낮춥니다" + 화면 "홍삼 함유" → 무관, conflict 아님

## 규칙
- 입력에 있는 쌍만 판정한다. 새 쌍을 만들지 않는다.
- conflict인 쌍만 출력한다. 쌍의 번호(pair)는 입력에 있는 것만 쓴다.

## 출력
JSON 객체만 출력한다. 다른 설명은 쓰지 않는다.
{"conflicts": [{"pair": 0, "reason": "효능을 확정적으로 말하지만 화면은 개인차를 단서로 단다"}]}
어긋나는 쌍이 없으면 {"conflicts": []}"""


def format_product_input(audio: dict, visual: dict) -> str:
    parts = ["## 음성 대본"]
    parts += [f"{s['t_start']:.1f}~{s['t_end']:.1f}초: {s['text']}" for s in audio["transcript"]]
    parts.append("\n## 화면 글자")
    texts = visual.get("screen_texts", [])
    parts += [f"{t['t_start']:.1f}~{t['t_end']:.1f}초: {t['text']}" for t in texts] or ["(없음)"]
    return "\n".join(parts)


def format_conflict_input(pairs: list[tuple[dict, dict]]) -> str:
    lines = ["## 같은 시각에 나온 음성 Claim · 화면 글자 쌍"]
    for i, (a, v) in enumerate(pairs):
        lines.append(f"[{i}] 음성({a['t_start']:.1f}~{a['t_end']:.1f}초): {a['text']}")
        lines.append(f"    화면({v['t_start']:.1f}~{v['t_end']:.1f}초): {v['text']}")
    return "\n".join(lines)


def parse_json_object(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"JSON 객체를 찾지 못함:\n{text}")
    return json.loads(text[start : end + 1])
