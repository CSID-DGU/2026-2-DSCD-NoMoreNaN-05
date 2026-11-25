"""클레임의 claim_type 목록. 한 클레임에 타입이 여러 개 붙을 수 있다.

예전 입력은 문자열 하나("EFFECT"), 지금 입력은 배열(["EFFECT", "QUANTITY"])이다. 둘 다 배열로 읽는다.
ETC는 주장이 아니라는 표시라 판정 대상 타입에서 뺀다. ETC만 붙어 있으면 클레임 전체를 주장으로 보지 않는다.
"""

QUANTITY = "QUANTITY"
COMPOSITION = "COMPOSITION"
CERTIFICATION = "CERTIFICATION"
EFFECT = "EFFECT"
PERSON_CREDENTIAL = "PERSON_CREDENTIAL"
ETC = "ETC"


def types_of(claim: dict) -> list[str]:
    """claim_type을 순서와 함께 배열로. 중복은 하나만 남긴다."""
    value = claim.get("claim_type")
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return list(dict.fromkeys(value))


def claim_types(claim: dict) -> list[str]:
    """ETC를 뺀 판정 대상 타입."""
    return [t for t in types_of(claim) if t != ETC]
