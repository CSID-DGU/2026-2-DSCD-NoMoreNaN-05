"""생성 모델에 보내는 프롬프트(prompt/<이름>.txt). 두 conda env에서 모두 import하므로 표준 라이브러리만 쓴다."""
import re
from pathlib import Path

DIR = Path(__file__).resolve().parent
_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def load(name: str, *placeholders: str) -> str:
    """prompt/<name>.txt. 끝의 개행 하나와 BOM은 프롬프트의 일부가 아니다.
    placeholders: 이 템플릿에 있어야 하는 {이름} 전부. 빠졌거나 모르는 이름이 있으면 ValueError."""
    text = (DIR / f"{name}.txt").read_text(encoding="utf-8-sig").removesuffix("\n")
    found = set(_PLACEHOLDER.findall(text))
    if found != set(placeholders):
        raise ValueError(f"prompt/{name}.txt 플레이스홀더 불일치: 있음 {sorted(found)}, 필요 {sorted(placeholders)}")
    return text


def render(text: str, **values: str) -> str:
    """{name}을 values[name]으로 한 번에 치환. 넣은 값은 다시 치환하지 않는다."""
    return _PLACEHOLDER.sub(lambda m: values[m.group(1)], text)
