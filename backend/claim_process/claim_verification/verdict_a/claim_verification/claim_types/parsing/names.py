"""제품명·회사명 비교용 정규화. 기호·공백을 빼고 소문자로 맞추며, 회사명은 법인 형태("주식회사", "㈜")도 뺀다."""

import re
import unicodedata

_COMPANY_FORM = re.compile(r"주식회사|유한회사|\(주\)|\(유\)|㈜")
_NOT_WORD = re.compile(r"[^0-9a-z가-힣]")


def normalize_name(text: str | None) -> str:
    return _NOT_WORD.sub("", unicodedata.normalize("NFKC", text or "").lower())


def normalize_company(text: str | None) -> str:
    return normalize_name(_COMPANY_FORM.sub("", unicodedata.normalize("NFKC", text or "")))
