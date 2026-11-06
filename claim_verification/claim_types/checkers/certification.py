"""CERTIFICATION 판정. 입력 DB(식약처 제품 정보)로 확인할 수 있는 주장만 대조한다.

    건강기능식품 표시      STTEMNT_NO가 있으면 SUPPORTED
    GMP                    INDUTY_CD_NM이 제조업이면 SUPPORTED (2020.12부터 제조업 의무라 간접 확인이다)
    인정번호 명시          RAWMTRL_STD_INFO·원재료 필드와 일치 SUPPORTED, 다르면 VIOLATION
    개별인정               인정번호가 있으면 SUPPORTED, 번호도 개별인정 분류도 없으면 VIOLATION, 분류만 있으면 UNCLEAR
    식약처 기능성 인정     MAIN_FNCTN에 있으면 SUPPORTED, 없으면 VIOLATION
    기능성 원료 X          RAWMTRL_STD_INFO에 있으면 SUPPORTED, 없으면 VIOLATION
    국내 최초·유일         식약처 제품 정보로 증명할 수 없어 UNCLEAR
    특허·해외 인증·출처·심의번호·판매 실적   OUT_OF_SCOPE

RAWMTRL_CLASS_INFO의 개별인정 분류는 인정번호와 어긋나는 제품이 많아 SUPPORTED의 근거로 쓰지 않는다.
다만 분류가 있으면 번호가 없어도 틀렸다고 단정하지 않는다("관절팔팔"은 번호 없이 개별인정으로 분류된다).
"""

import re

from ...finding import SUPPORTED, UNCLEAR, VIOLATION
from ..parsing.lexicon import ingredient_key, split_ingredients
from ..parsing.units import normalize_text
from ..result import OUT_OF_SCOPE, Check

HFF_ON_RECORD = "HFF_ON_RECORD"
SOURCE_OR_REVIEW = "SOURCE_OR_REVIEW"
SALES_OR_RANK = "SALES_OR_RANK"
OTHER_CERTIFICATION = "OTHER_CERTIFICATION"
GMP_BY_INDUSTRY = "GMP_BY_INDUSTRY"
GMP_NOT_CONFIRMED = "GMP_NOT_CONFIRMED"
RECOGNITION_NO_MATCHES = "RECOGNITION_NO_MATCHES"
RECOGNITION_NO_MISMATCH = "RECOGNITION_NO_MISMATCH"
RECOGNITION_ON_PRODUCT = "RECOGNITION_ON_PRODUCT"
RECOGNITION_UNCONFIRMED = "RECOGNITION_UNCONFIRMED"
RECOGNITION_ABSENT = "RECOGNITION_ABSENT"
FUNCTION_NOT_ON_RECORD = "FUNCTION_NOT_ON_RECORD"
FUNCTIONAL_INGREDIENT_ABSENT = "FUNCTIONAL_INGREDIENT_ABSENT"
FIRST_CLAIM_UNPROVABLE = "FIRST_CLAIM_UNPROVABLE"
INGREDIENT_ON_RECORD = "INGREDIENT_ON_RECORD"
INGREDIENT_NOT_CONFIRMED = "INGREDIENT_NOT_CONFIRMED"
FUNCTION_ON_RECORD = "FUNCTION_ON_RECORD"
FUNCTION_NOT_CONFIRMED = "FUNCTION_NOT_CONFIRMED"
FUNCTIONAL_INGREDIENT_ON_RECORD = "FUNCTIONAL_INGREDIENT_ON_RECORD"
CERTIFICATION_UNCLASSIFIED = "CERTIFICATION_UNCLASSIFIED"

_HFF_LABEL = re.compile(
    r"\W*(?:(?:본|이)\s*(?:제품|광고|영상)[은는]\s*|광고방송\s*/\s*|[0-9A-Za-z가-힣]{1,12}[은는]\s*)?"
    r"건강기능\s*식품\s*(?:전품목\s*)?(?:광고)?\s*(?:입니다)?\W*"
    r"(?:광고심의필.*|MAT-KR.*|식품의약품안전처\W*)?", re.IGNORECASE | re.DOTALL)
_SOURCE = re.compile(r"출처|journal|et al|randomized|double blind|study|인체\s*적용\s*시험|시험\s*(?:조건|기관|방법|결과)|이중맹검|"
                     r"보고서|실태\s*조사|소비자\s*조사|생산\s*실적|판매\s*실적|심의|mat-kr|-pm-kr|논문|vol\.?\s*\d", re.IGNORECASE)
# 날짜 각주. "국내최초 ... *2022년 8월 기준"은 최초 주장이 본문이라 여기에 넣지 않는다.
_DATE_NOTE = re.compile(r"\d{4}\s*년.*기준\s*$")
_SALES = re.compile(r"\d\s*위\b|\d\s*등\b|구매율|구매량|구매액|판매량|판매처|점유|database", re.IGNORECASE)
_OTHER = re.compile(r"특허|patent|haccp|해썹|fda|\bndi\b|\biso\b|ifos|gras|\bnsf\b|\busp\b|vegan|비건|브이라벨|v-label|non\s*-?gmo|유기농|"
                    r"할랄|orivo|iffo|goed|ccm|신기술|institute|어워드|수상|일류상품|국제\s*인증", re.IGNORECASE)
_GMP = re.compile(r"(?<![A-Za-z])gmp(?![A-Za-z])|우수건강기능식품제조기준", re.IGNORECASE)
_NUMBER = re.compile(r"(?<!\d)(\d{4})\s*-\s*(\d{1,3})\s*호")
# "인정번호 제2006-17"처럼 호가 빠져도 "제"나 "인정번호"가 앞에 있으면 번호다.
_NUMBER_NO_HO = re.compile(r"(?:제|인정번호)\s*(\d{4})\s*-\s*(\d{1,3})(?!\d)")
_RCOGN_NO = re.compile(r"(\d{4})\s*-\s*(\d{1,3})")
_FIRST = re.compile(r"최초|유일|독점|개별\s*인정형?\s*\d+\s*호")
# "국내 최초 체지방 감소 유산균"의 체지방 감소
_FIRST_FUNCTION = re.compile(r".*(?:최초|유일)\W*(?P<fn>[가-힣]+(?:\s[가-힣]+)*?)\s*(?:기능성\s*)?(?:유산균|프로바이오틱스|건강기능식품)", re.S)
_MICROBE_WORD = re.compile(r"유산균|프로바이오틱스")
_MICROBE_FIELD = re.compile(r"유산균|프로바이오틱스|lactobacillus|lactiplantibacillus|bifidobacterium|streptococcus", re.I)
_INDIVIDUAL = re.compile(r"개별\s*인정")
_APPROVED = re.compile(r"(?:식약처|식품의약품안전처|기능성).*인정|인정.*기능성")
# 앞에 숫자가 붙은 말("2중 기능성")은 기능 이름이 아니다.
_FUNCTION_WORD = re.compile(r"(?<![0-9가-힣])([가-힣]+(?:\s*[가-힣]+)?)\s*기능성")
_FUNCTION_COUNT = re.compile(r"\d\s*(?:가지|대|종)\s*기능성")
_FUNCTIONAL_INGREDIENT = re.compile(r"기능성\s*원료")
# "기능성 인정 일일섭취량, 루테인으로서 10~20mg/일"은 기능이 아니라 섭취량 기준을 말한다.
_INTAKE_REFERENCE = re.compile(r"일일\s*섭취량|1일\s*섭취량")
_HFF_SENTENCE = re.compile(r"건강기능\s*식품입니다\W*$")
_HELP_PHRASE = re.compile(r"([가-힣]+(?:\s+[가-힣]+)?)에\s*도움")
# 제품 근거는 원료가 인정받았다는 것만 보여 준다. "직접", "자체" 인정한 주체는 확인할 수 없다.
_ISSUER = re.compile(r"직접|자체")
# "배뇨건강"과 신고 문구 "배뇨기능 개선"은 같은 기능이다. 끝말을 빼고 핵심어로 비교한다.
_FUNCTION_ENDING = re.compile(r"(?:건강|기능|개선|증진|케어)+$")
_NOT_FUNCTION_WORD = re.compile(r"식약처|식품의약품안전처|국내|최초|유일|이중|인정|받은|어린이|에서$|있는$|주는$|도움|수$|건강기능식품")
_WORD = re.compile(r"[^0-9a-z가-힣]")
_MIN_NAME = 2


def check_certification(claim: dict, product: dict) -> list[Check]:
    text = normalize_text(claim["text"])
    db = product["DB"]["CERTIFICATION"]
    if _HFF_LABEL.fullmatch(text):
        return [_hff(text, db)]
    if _SOURCE.search(text) or (_DATE_NOTE.search(text) and not _FIRST.search(text)):
        return [Check(OUT_OF_SCOPE, SOURCE_OR_REVIEW, "출처·시험·심의 안내는 제품 근거로 검증하지 않음")]
    if _SALES.search(text):
        return [Check(OUT_OF_SCOPE, SALES_OR_RANK, "순위·판매 주장은 제품 근거로 검증하지 않음")]
    if _OTHER.search(text):
        return [Check(OUT_OF_SCOPE, OTHER_CERTIFICATION, "특허·해외 인증 등은 식약처 제품 정보로 검증할 수 없음")]
    if _GMP.search(text):
        return [_gmp(text, db)]
    checks = _recognition_number(text, db)
    if _FIRST.search(text):
        checks.append(Check(UNCLEAR, FIRST_CLAIM_UNPROVABLE, "'국내 최초·유일' 여부는 식약처 제품 정보로 확인할 수 없음", claim_value=text,
                            evidence=[{"field": "PRMS_DT", "value": db["PRMS_DT"]}]))
    if not _numbers(text):
        if _INDIVIDUAL.search(text):
            checks.append(_individual(claim, text, db))
        elif _APPROVED.search(text):
            checks.append(_function_approved(text, db))
        elif _FUNCTIONAL_INGREDIENT.search(text):
            checks.append(_functional_ingredient(claim, text, db))
    if _FIRST.search(text):
        checks.extend(_first_claim_parts(claim, text, db, checks))
    if not checks and _HFF_SENTENCE.search(text):
        return [_hff(text, db)]
    return checks or [Check(UNCLEAR, CERTIFICATION_UNCLASSIFIED, "식약처 제품 정보에서 대조할 항목을 정할 수 없는 인증 주장", claim_value=text)]


def _first_claim_parts(claim: dict, text: str, db: dict, checks: list[Check]) -> list[Check]:
    """최초 여부는 몰라도 원료와 기능은 확인한다. "유산균은 들어 있으나 국내 최초인지는 알 수 없음"이 되게 한다."""
    parts = []
    entries = [e[k] or "" for e in db["RAWMTRL_STD_INFO"] for k in ("RAWMTRL_NM", "SKLL_IX_IRDNT_RAWMTRL") if k in e]
    names = [*split_ingredients(db["RAWMTRL_NM"]), *split_ingredients(db["INDIV_RAWMTRL_NM"]), *entries]
    evidence = [{"field": "RAWMTRL_NM", "value": db["RAWMTRL_NM"]}]

    def ingredient(name: str, found: bool) -> Check:
        if found:
            return Check(SUPPORTED, INGREDIENT_ON_RECORD, "제품 원재료에서 확인", target=name, claim_value=name, evidence=evidence)
        return Check(UNCLEAR, INGREDIENT_NOT_CONFIRMED, "제품 원재료에서 확인되지 않음", target=name, claim_value=name, evidence=evidence)

    listed = claim.get("ingredients") or []
    parts.extend(ingredient(name, any(_same_name(name, n) for n in names)) for name in listed)
    microbe = _MICROBE_WORD.search(text)
    if microbe and not listed:
        parts.append(ingredient(microbe[0], bool(_MICROBE_FIELD.search(" ".join(names)))))
    if len(checks) == 1:
        m = _FIRST_FUNCTION.match(text)
        word = _compact(m["fn"]) if m else ""
        if len(word) >= _MIN_NAME:
            found = word in _compact(db["MAIN_FNCTN"])
            parts.append(Check(SUPPORTED if found else UNCLEAR, FUNCTION_ON_RECORD if found else FUNCTION_NOT_CONFIRMED,
                               "제품에 신고된 기능성에서 확인" if found else "제품에 신고된 기능성에서 확인되지 않음",
                               target=m["fn"], claim_value=m["fn"], evidence=[{"field": "MAIN_FNCTN", "value": db["MAIN_FNCTN"]}]))
    return parts


def _hff(text: str, db: dict) -> Check:
    evidence = [{"field": "STTEMNT_NO", "value": db["STTEMNT_NO"]}]
    return Check(SUPPORTED, HFF_ON_RECORD, "건강기능식품으로 신고된 제품", claim_value=text, evidence=evidence)


def _gmp(text: str, db: dict) -> Check:
    evidence = [{"field": "INDUTY_CD_NM", "value": db["INDUTY_CD_NM"]}]
    if "건강기능식품" in db["INDUTY_CD_NM"] and "제조" in db["INDUTY_CD_NM"]:
        return Check(SUPPORTED, GMP_BY_INDUSTRY, "건강기능식품 제조업이라 GMP 대상(업종으로 간접 확인)", claim_value=text, evidence=evidence)
    return Check(UNCLEAR, GMP_NOT_CONFIRMED, "업종으로 GMP 대상인지 확인할 수 없음", claim_value=text, evidence=evidence)


def _numbers(text: str) -> set[tuple[str, int]]:
    text = normalize_text(text)
    return {(m[0], int(m[1])) for pattern in (_NUMBER, _NUMBER_NO_HO) for m in pattern.findall(text)}


def _product_numbers(db: dict) -> dict[tuple[str, int], str]:
    """{(연도, 번호): 원료명}. RCOGN_NO는 "2010-35" 꼴이고, 원재료 필드는 "(제2010-35호)" 꼴이다."""
    numbers = {}
    for entry in db["RAWMTRL_STD_INFO"]:
        m = _RCOGN_NO.search(entry["RCOGN_NO"] or "")
        if m:
            numbers.setdefault((m[1], int(m[2])), entry["RAWMTRL_NM"])
    for field in ("RAWMTRL_NM", "INDIV_RAWMTRL_NM"):
        for token in normalize_text(db[field]).split(","):
            for number in _numbers(token):
                numbers.setdefault(number, token.strip())
    return numbers


def _recognition_number(text: str, db: dict) -> list[Check]:
    claimed = _numbers(text)
    if not claimed:
        return []
    numbers = _product_numbers(db)
    evidence = [{"field": "RAWMTRL_STD_INFO", "value": ", ".join(f"제{y}-{n}호 {name}" for (y, n), name in numbers.items())}]
    checks = []
    for number in sorted(claimed):
        value = f"제{number[0]}-{number[1]}호"
        if number in numbers:
            checks.append(Check(SUPPORTED, RECOGNITION_NO_MATCHES, "제품의 인정번호와 일치", target=numbers[number], claim_value=value,
                                evidence=evidence))
        else:
            checks.append(Check(VIOLATION, RECOGNITION_NO_MISMATCH, "제품의 인정번호에 없음", claim_value=value, evidence=evidence))
    return checks


def _individual(claim: dict, text: str, db: dict) -> Check:
    numbers = _product_numbers(db)
    evidence = [{"field": "RAWMTRL_STD_INFO", "value": ", ".join(numbers.values())}]
    if not numbers:
        classes = [{"field": "RAWMTRL_CLASS_INFO", "value": e["MLSFC_NM"]} for e in db["RAWMTRL_CLASS_INFO"] if "개별" in (e["MLSFC_NM"] or "")]
        if classes:
            return Check(UNCLEAR, RECOGNITION_UNCONFIRMED, "개별인정 분류는 있지만 인정번호를 찾지 못함", claim_value=text, evidence=classes[:1])
        return Check(VIOLATION, RECOGNITION_ABSENT, "인정번호도 개별인정 분류도 없음", claim_value=text,
                     evidence=[{"field": "RAWMTRL_NM", "value": db["RAWMTRL_NM"]}])
    if _ISSUER.search(text):
        return Check(UNCLEAR, RECOGNITION_UNCONFIRMED, "인정받은 원료는 있지만 인정받은 주체는 확인할 수 없음", claim_value=text,
                     evidence=evidence)
    names = claim.get("ingredients") or []
    if names and not any(_same_name(n, v) for n in names for v in numbers.values()):
        return Check(UNCLEAR, RECOGNITION_UNCONFIRMED, "광고한 원료의 개별인정 번호를 찾지 못함", target=", ".join(names), claim_value=text,
                     evidence=evidence)
    return Check(SUPPORTED, RECOGNITION_ON_PRODUCT, "제품에 개별인정 번호가 있는 원료가 있음", claim_value=text, evidence=evidence)


def _same_name(a: str, b: str) -> bool:
    x, y = ingredient_key(a), ingredient_key(b)
    return len(x) >= _MIN_NAME and len(y) >= _MIN_NAME and (x in y or y in x)


def _function_approved(text: str, db: dict) -> Check:
    evidence = [{"field": "MAIN_FNCTN", "value": db["MAIN_FNCTN"]}]
    if not db["MAIN_FNCTN"]:
        return Check(UNCLEAR, FUNCTION_NOT_CONFIRMED, "제품에 신고된 기능성을 찾지 못함", claim_value=text)
    if _INTAKE_REFERENCE.search(text):
        return Check(UNCLEAR, FUNCTION_NOT_CONFIRMED, "기능이 아니라 섭취량 기준을 말하는 문장이라 기능성과 대조할 수 없음", claim_value=text,
                     evidence=evidence)
    if _FUNCTION_COUNT.search(text):
        return Check(UNCLEAR, FUNCTION_NOT_CONFIRMED, "기능성 개수는 무엇을 세었는지 알 수 없음", claim_value=text, evidence=evidence)
    for word in _function_words(text):
        if word not in _compact(db["MAIN_FNCTN"]):
            return Check(VIOLATION, FUNCTION_NOT_ON_RECORD, f"신고된 기능성에 {word} 없음", claim_value=text, evidence=evidence)
    return Check(SUPPORTED, FUNCTION_ON_RECORD, "제품에 신고된 기능성이 있음", claim_value=text, evidence=evidence)


def _function_words(text: str) -> list[str]:
    """"식약처 근력개선 기능성 인정"의 근력. 수식어를 뺀 마지막 단어의 핵심어만 본다."""
    words = []
    for phrase in _FUNCTION_WORD.findall(text):
        last = phrase.split()[-1]
        if not _NOT_FUNCTION_WORD.search(last):
            words.append(_core_word(last))
    words.extend(_core_word(phrase) for phrase in _HELP_PHRASE.findall(text))
    return [w for w in words if w]


def _core_word(word: str) -> str:
    return _FUNCTION_ENDING.sub("", _compact(word))


def _compact(text: str) -> str:
    return _WORD.sub("", normalize_text(text).lower())


def _functional_ingredient(claim: dict, text: str, db: dict) -> Check:
    entries = [e["RAWMTRL_NM"] for e in db["RAWMTRL_STD_INFO"]]
    names = claim.get("ingredients") or [e for e in entries if len(_compact(e)) >= _MIN_NAME and _compact(e) in _compact(text)]
    evidence = [{"field": "RAWMTRL_STD_INFO", "value": ", ".join(entries)}]
    if names and all(any(_same_name(n, e) for e in entries) for n in names):
        return Check(SUPPORTED, FUNCTIONAL_INGREDIENT_ON_RECORD, "제품의 기능성 원료에 있음", target=", ".join(names), claim_value=text,
                     evidence=evidence)
    if not names or not entries:
        return Check(UNCLEAR, FUNCTION_NOT_CONFIRMED, "어떤 원료를 말하는지 또는 제품의 기능성 원료를 알 수 없음", claim_value=text,
                     evidence=evidence)
    return Check(VIOLATION, FUNCTIONAL_INGREDIENT_ABSENT, "제품의 기능성 원료에 없음", target=", ".join(names), claim_value=text,
                 evidence=evidence)
