"""QUANTITY 판정. 세부 분류 → 같은 기준의 근거와 대조.

    SALES·STUDY          가격·순위·판매, 시험 조건은 제품 근거로 검증하지 않는다(OUT_OF_SCOPE).
    PACKAGE              포장 규격은 제품 사실이지만 근거가 없다(UNCLEAR).
    RANGE                "10~20mg/일"은 제품 함량이 아니라 기준 범위다(UNCLEAR).
    PERCENT              "철 3 mg(25 %)"은 별표 5로 검산, "판토텐산 544%"는 표시량으로 확인한다.
    AMOUNT               "아연 12mg"은 BASE_STANDARD 표시량, 그다음 하루 함량과 비교한다.
    INTAKE·SHELF·HERITAGE  SRV_USE, DISTB_PD, BSSH_PRMS_DT와 비교한다.

함량은 광고 수치가 어느 기준인지 모르므로 그럴듯한 기준(표시량, 1일 횟수·1회 개수를 곱하거나 나눈 값,
하루 함량)을 모두 본다. 어디에도 맞지 않을 때만 VIOLATION이다. 균수와 농도 표기(분모 1 g, 100 g)는
기준을 정할 수 없어 UNCLEAR다.
"""

import re

from ...finding import SUPPORTED, UNCLEAR, VIOLATION
from ..parsing.intake import Intake, parse_intake
from ..parsing.lexicon import ingredient_key
from ..parsing.names import normalize_company
from ..parsing.nutrients import canonical, daily_value
from ..parsing.spec import SpecItem, daily_amount, parse_spec
from ..parsing.units import (NUM_START, NUMBER, UNIT, Amount, comparable, make_basis, make_unit, normalize_text,
                             parse_amounts, same_amount, scaled_number, to_number)
from ..result import OUT_OF_SCOPE, Check

# 사유 코드
SALES_OR_RANK = "SALES_OR_RANK"
STUDY_CONDITION = "STUDY_CONDITION"
PACKAGE_NOT_IN_EVIDENCE = "PACKAGE_NOT_IN_EVIDENCE"
REFERENCE_RANGE = "REFERENCE_RANGE"
REFERENCE_CLAIM = "REFERENCE_CLAIM"
COMPARISON_NOT_VERIFIED = "COMPARISON_NOT_VERIFIED"
NUTRIENT_UNRESOLVED = "NUTRIENT_UNRESOLVED"
PERCENT_CONSISTENT = "PERCENT_CONSISTENT"
PERCENT_MISMATCH = "PERCENT_MISMATCH"
PERCENT_MATCHES_LABEL = "PERCENT_MATCHES_LABEL"
PERCENT_NOT_CONFIRMED = "PERCENT_NOT_CONFIRMED"
INFANT_PRODUCT = "INFANT_PRODUCT"
BASIS_MISMATCH = "BASIS_MISMATCH"
SPEC_NOT_FOUND = "SPEC_NOT_FOUND"
AMOUNT_MATCHES_LABEL = "AMOUNT_MATCHES_LABEL"
AMOUNT_MATCHES_DAILY = "AMOUNT_MATCHES_DAILY"
AMOUNT_MATCHES_SERVING = "AMOUNT_MATCHES_SERVING"
AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
MULTIPLE_VALUES = "MULTIPLE_VALUES"
INTAKE_MATCHES = "INTAKE_MATCHES"
INTAKE_MISMATCH = "INTAKE_MISMATCH"
INTAKE_UNIT_DIFFERS = "INTAKE_UNIT_DIFFERS"
INTAKE_NOT_FOUND = "INTAKE_NOT_FOUND"
SHELF_LIFE_MATCHES = "SHELF_LIFE_MATCHES"
SHELF_LIFE_MISMATCH = "SHELF_LIFE_MISMATCH"
SHELF_LIFE_NOT_COMPARABLE = "SHELF_LIFE_NOT_COMPARABLE"
HERITAGE_NOT_CONFIRMED = "HERITAGE_NOT_CONFIRMED"
HERITAGE_NOT_MANUFACTURER = "HERITAGE_NOT_MANUFACTURER"
COUNT_NOT_VERIFIED = "COUNT_NOT_VERIFIED"
FOOTNOTE = "FOOTNOTE"
QUANTITY_UNCLASSIFIED = "QUANTITY_UNCLASSIFIED"

_SALES = re.compile(r"\d\s*(?:만\s*)?원|할인|특가|쿠폰|적립|가격|인하|증정|무료|\d\s*위\b|\d\s*등\b|no\.?\s*1\b|top\s*\d|순위|"
                    r"리뷰|후기|평점|별점|구매|구입|판매|누적|출고|재구매|수량|소진|매출", re.IGNORECASE)
_STUDY = re.compile(r"시험|임상|섭취군|대조군|섭취\s*그룹|이중맹검|대상자|인원\s*:|\d\s*명\b|투여|/\s*day|mg\s*/\s*kg|p\s*<|논문|연구\s*결과|"
                    r"(?:증가|감소|개선|향상)\s*(?:확인|효과)|\d\s*배\s*증가", re.IGNORECASE)
_STUDY_BASIS = re.compile(r"시험|섭취군|대조군|연구")
_PACKAGE = re.compile(r"\d\s*(?:정|캡슐|포|병|알|개|ml|mg|g)?\s*[xX×*]\s*\d|개월분|일치|회분|\d\s*(?:정|캡슐|포|병|구미|팩|매)\s*[(,/]|"
                      r"^\s*총\s*\d", re.IGNORECASE)
_PACKAGE_BASIS = re.compile(r"포장|내용량|총량")
_DAILY_LABEL = re.compile(r"(?:1\s*일|하루)\s*섭취\s*(?:권장)?량(?:은)?\s*[:：]?\s*\d")
_FOOTNOTE = re.compile(r"수치는.*비율")
# 제품 함량과 같아도 "식약처 고시 최소 기준", "최고함량" 자체가 맞다는 뜻은 아니다.
_REFERENCE = re.compile(r"고시|최소\s*기준|최대\s*함량|최고\s*함량|기능성\s*인정")
_COMPARISON = re.compile(r"\d\s*배|함량\s*대비|제품\s*대비")
_CFU_WORD = re.compile(r"cfu|\d\s*억", re.IGNORECASE)
_RANGE = re.compile(rf"(?:{NUMBER})\s*(?:{UNIT})?\s*[~∼-]\s*(?:{NUMBER})\s*(?:{UNIT})", re.IGNORECASE)
_PERCENT = re.compile(rf"{NUM_START}(?P<pct>{NUMBER})\s*%")
_AMOUNT_PCT = re.compile(
    rf"{NUM_START}(?P<num>{NUMBER})\s*(?P<unit>{UNIT})(?:\s*(?P<basis>[αa]-?te|rae|re|ne|dfe)(?![a-z]))?\s*[(\s]\s*"
    rf"(?P<pct>{NUMBER})\s*%", re.IGNORECASE)
_LARGE_ONLY = re.compile(rf"{NUM_START}(?P<num>{NUMBER})\s*(?P<large>억|조)(?!\s*(?:cfu|마리))", re.IGNORECASE)
_PAREN = re.compile(r"\([^()]*\)")
_GROUP_SPLIT = re.compile(r"[,/·]|\s및\s|\s&\s")
_VITAMIN_LETTER = re.compile(r"[A-Ka-k]\d*")
_VITAMIN_B = re.compile(r"[Bb]\d+")
_LAST_WORD = re.compile(r"[0-9A-Za-z가-힣]+")
_NAME_SPLIT = re.compile(r"[,:：/\n·;]")
_INFANT = re.compile(r"영유아|영·유아|베이비|baby|유아용|아기", re.IGNORECASE)
_KOREAN_COUNT = re.compile(r"(?<![가-힣])(한|두|세|네)\s*(번|회|포|정|알|캡슐|스틱|병|환|앰플)")
_KOREAN_NUMBER = {"한": "1", "두": "2", "세": "3", "네": "4"}
_DAILY_WORDS = re.compile(r"(?:하루에?|1\s*일)\s*(?:단\s*)?(?:섭취\s*(?:권장)?량(?:은)?\s*[:：]?\s*)?")
_INTAKE_HINT = re.compile(r"(?:하루|1\s*일|1\s*회)")
_SHELF = re.compile(r"소비기한|유통기한")
# "2027년까지"는 기간이 아니라 날짜다. 네 자리 연도는 기간으로 읽지 않는다.
_MONTHS = re.compile(r"(?<!\d)(\d{1,3})\s*(개월|년)")
_HERITAGE = re.compile(r"(\d+)\s*년\s*(?:전통|역사|노하우)")
# 비타민D만 환산이 하나로 정해진다(1 μg = 40 IU). 비타민A·E는 원료 형태에 따라 환산값이 달라 하지 않는다.
IU_PER_UG_VITAMIN_D = 40
_DV_WORD = re.compile(r"기준치|영양성분")
_MICROBE = re.compile(r"프로바이오틱스|유산균|생균")
_COUNT = re.compile(r"\d\s*(?:종|가지)")
_OIL = re.compile(r"유지|오일|oil", re.IGNORECASE)
_NAME_INNER = re.compile(r"\(([^()]*)\)")

# 표시량 이름과 광고 이름이 다른 합계 표기
_SUM_NAMES = {"epa와dha의합": "epadha", "epa및dha의합": "epadha", "epa및dha합": "epadha", "epa및dha": "epadha",
              "epadha": "epadha", "epadha의합": "epadha"}
CONCENTRATION_PER = {1.0, 100.0}
_GENERIC_PILL = "알"
_PILLS = {"정", "캡슐", "환"}


def check_quantity(claim: dict, product: dict) -> list[Check]:
    text = normalize_text(claim["text"])
    basis = normalize_text(claim.get("intake_basis"))
    db = product["DB"]["QUANTITY"]
    if _SALES.search(text):
        return [Check(OUT_OF_SCOPE, SALES_OR_RANK, "가격·판매·순위 주장은 제품 근거로 검증하지 않음")]
    if _STUDY.search(text) or _STUDY_BASIS.search(basis):
        return [Check(OUT_OF_SCOPE, STUDY_CONDITION, "시험 조건·결과는 제품 근거로 검증하지 않음")]
    if _SHELF.search(text):
        return _check_shelf_life(text, db)
    if _HERITAGE.search(text):
        return _check_heritage(text, product, db)
    if _FOOTNOTE.search(text):
        return [Check(OUT_OF_SCOPE, FOOTNOTE, "수치 기준을 설명하는 각주")]
    if _REFERENCE.search(text) or _REFERENCE.search(basis):
        return [Check(UNCLEAR, REFERENCE_CLAIM, "고시 기준·최고함량 주장은 제품 표시량만으로 확인할 수 없음", claim_value=text)]
    if _COMPARISON.search(text) or _COMPARISON.search(basis):
        return [Check(UNCLEAR, COMPARISON_NOT_VERIFIED, "비교 대상의 근거가 없어 확인할 수 없음", claim_value=text)]
    if not _DAILY_LABEL.search(text) and not _CFU_WORD.search(text) and (
            _PACKAGE.search(text) or _PACKAGE_BASIS.search(basis)):
        return [Check(UNCLEAR, PACKAGE_NOT_IN_EVIDENCE, "포장 규격은 식약처 제품 정보에 없어 확인할 수 없음")]
    if _RANGE.search(text):
        return [Check(UNCLEAR, REFERENCE_RANGE, "범위 표기는 제품 함량이 아니라 기준 범위라 비교할 수 없음")]
    items = parse_spec(db["BASE_STANDARD"])
    intake = parse_intake(db["SRV_USE"])
    aliases = _std_aliases(db)
    checks = _check_percent(claim, text, product, items, intake)
    if checks:
        return checks
    checks = _check_amount(claim, text, items, intake, aliases)
    if checks:
        return checks
    if _INTAKE_HINT.search(text):
        checks = _check_intake(text, intake, db)
        if checks:
            return checks
    if _COUNT.search(text):
        return [Check(UNCLEAR, COUNT_NOT_VERIFIED, "성분·기능의 개수는 무엇을 세었는지 알 수 없어 확인할 수 없음")]
    return [Check(UNCLEAR, QUANTITY_UNCLASSIFIED, "대조할 근거 필드를 정할 수 없는 수치 주장")]


# ---------- 공통 ----------

def _key(name: str | None) -> str:
    key = ingredient_key(name)
    key = key[1:] if key.startswith("총") and len(key) > 2 else key
    return _SUM_NAMES.get(key, key)


def _spec_evidence(item: SpecItem) -> list[dict]:
    return [{"field": "BASE_STANDARD", "value": item.line}]


def _name_keys(item: SpecItem) -> set[str]:
    """표시량 이름의 비교 키. "엠에스엠(MSM)"은 전체, 괄호 앞, 괄호 안 이름으로 모두 찾는다."""
    names = [item.name, _NAME_INNER.sub("", item.name)]
    for inner in _NAME_INNER.findall(item.name):
        names.extend(inner.split(","))
    return {k for k in map(_key, names) if k}


def _std_aliases(db: dict) -> dict[str, str]:
    """제품 RAWMTRL_STD_INFO의 "엠에스엠(MSM)"에서 {msm: 엠에스엠}. 그 제품이 스스로 밝힌 이름만 믿는다."""
    aliases = {}
    for entry in db["RAWMTRL_STD_INFO"]:
        name = normalize_text(entry["RAWMTRL_NM"])
        for inner in _NAME_INNER.findall(name):
            for alias in inner.split(","):
                aliases[_key(alias)] = _key(_NAME_INNER.sub("", name))
    return aliases


def _find_items(name: str | None, items: list[SpecItem], aliases: dict[str, str] | None = None) -> list[SpecItem]:
    key = _key(name)
    keys = {key, (aliases or {}).get(key, key)}
    return [i for i in items if key and keys & _name_keys(i)]


def _mentioned_items(text: str, items: list[SpecItem], aliases: dict[str, str]) -> list[SpecItem]:
    """성분명이 문장에 그대로 나오는 표시량 항목. 합계 이름은 기름 무게("EPA 및 DHA 함유 유지")에 쓰지 않는다."""
    found = []
    for item in items:
        keys = _name_keys(item)
        if "epadha" in keys:
            keys = set() if _OIL.search(text) else keys | set(_SUM_NAMES)
        keys = keys | {alias for alias, base in aliases.items() if base in keys}
        if any(len(k) >= 2 and _key_pattern(k).search(text.lower()) for k in keys):
            found.append(item)
    return found


def _key_pattern(key: str) -> re.Pattern:
    """글자 사이 공백·기호를 허용한다. 숫자로 끝나는 이름은 뒤 숫자를 막는다(비타민B1이 비타민B12에 걸리지 않게)."""
    return re.compile(r"[^0-9a-zα-ω가-힣]*".join(map(re.escape, key)) + (r"(?!\d)" if key[-1].isdigit() else ""))


def _claim_items(claim: dict, text: str, items: list[SpecItem], amounts: list[Amount],
                 aliases: dict[str, str]) -> list[SpecItem]:
    found = []
    for name in claim.get("ingredients") or []:
        for item in _find_items(name, items, aliases):
            if item not in found:
                found.append(item)
    found = found or _mentioned_items(text, items, aliases)
    if not found and amounts and all(a.unit == "CFU" for a in amounts):
        found = [i for i in items if i.amount.unit == "CFU"]
    return found


def _is_infant(product: dict) -> bool:
    names = f"{product.get('product_name') or ''} {product['match'].get('matched_name') or ''}"
    return bool(_INFANT.search(normalize_text(names)))


# ---------- % ----------

def _check_percent(claim: dict, text: str, product: dict, items: list[SpecItem], intake: Intake | None) -> list[Check]:
    pairs = list(_AMOUNT_PCT.finditer(text))
    if pairs:
        return [c for i, m in enumerate(pairs)
                for c in _check_amount_percent(claim, text, m, pairs[i - 1].end() if i else 0, product, items, intake)]
    grouped = _check_grouped_percent(text, product, items)
    if grouped:
        return grouped
    percents = _PERCENT.findall(text)
    ingredients = claim.get("ingredients") or []
    # "영국산 100%", "일일 섭취량 대비 100%"는 영양성분 %가 아니다. 기준치를 말할 때만 원료 하나에 붙인다.
    has_reference = _DV_WORD.search(text) or _DV_WORD.search(normalize_text(claim.get("intake_basis")))
    if has_reference and len(percents) == 1 and len(ingredients) == 1 and canonical(ingredients[0]):
        return _check_label_percent(ingredients[0], to_number(percents[0]), product, items)
    return []


def _check_grouped_percent(text: str, product: dict, items: list[SpecItem]) -> list[Check]:
    """"판토텐산 500%, 비타민C, D, E, K 100%"처럼 이름 뒤에 %가 오는 나열. 이름을 하나도 못 읽으면 대상이 아니다."""
    checks, resolved, start = [], False, 0
    for m in _PERCENT.finditer(text):
        for token, nutrient in _grouped_names(text[start:m.start()]):
            if nutrient is None:
                checks.append(Check(UNCLEAR, NUTRIENT_UNRESOLVED, "영양성분을 특정할 수 없어 %를 확인할 수 없음", target=token,
                                    claim_value=f"{m['pct']}%"))
            else:
                resolved = True
                checks.extend(_check_label_percent(nutrient, to_number(m["pct"]), product, items))
        start = m.end()
    return checks if resolved else []


def _grouped_names(prefix: str) -> list[tuple[str, str | None]]:
    """앞 조각의 이름들. "비타민C, D"의 D처럼 글자만 있으면 앞의 비타민에 붙인다."""
    out, vitamin = [], False
    for token in _GROUP_SPLIT.split(prefix):
        token = token.strip()
        if not token:
            continue
        last = _LAST_WORD.findall(token)[-1] if _LAST_WORD.search(token) else token
        nutrient = canonical(token) or canonical(last) or (canonical(f"비타민{last}") if _VITAMIN_B.fullmatch(last) else None)
        if nutrient is None and vitamin and _VITAMIN_LETTER.fullmatch(last):
            nutrient = canonical(f"비타민{last}")
        vitamin = bool(nutrient and nutrient.startswith("비타민"))
        out.append((token, nutrient))
    return out


def _nutrient_name(claim: dict, prefix: str) -> str | None:
    """수치 바로 앞 조각에서 영양성분 이름을 찾는다. 없으면 클레임의 원료가 하나일 때 그 원료를 쓴다."""
    last = _NAME_SPLIT.split(prefix)[-1].strip()
    for candidate in (last, *reversed(last.split())):
        if canonical(candidate):
            return candidate
    ingredients = claim.get("ingredients") or []
    return ingredients[0] if len(ingredients) == 1 and canonical(ingredients[0]) else None


def _check_amount_percent(claim, text, m, start, product, items, intake) -> list[Check]:
    name = _nutrient_name(claim, text[start:m.start()])
    amount = Amount(to_number(m["num"]), make_unit(m["unit"]), make_basis(m["basis"]))
    claimed = to_number(m["pct"])
    value = f"{m['num']} {m['unit']} ({m['pct']}%)"
    reference = daily_value(name)
    if reference is None:
        return [Check(UNCLEAR, BASIS_MISMATCH, "별표 5에 없는 성분이거나 성분명을 알 수 없어 %를 검산할 수 없음",
                      target=name, claim_value=value)]
    target = canonical(name)
    annex = [{"field": "별표 5", "value": f"{target} {reference.value:g} {reference.unit}"}]
    if _is_infant(product):
        return [Check(UNCLEAR, INFANT_PRODUCT, "영유아용 제품은 별표 5 기준치를 그대로 적용하지 않음",
                      target=target, claim_value=value, evidence=annex)]
    if not comparable(amount, reference):
        return [Check(UNCLEAR, BASIS_MISMATCH, f"광고 단위({amount.unit} {amount.basis or ''})와 별표 5 기준이 달라 검산할 수 없음",
                      target=target, claim_value=value, evidence=annex)]
    computed = amount.base()[1] / reference.base()[1] * 100
    # 표시 함량과 %는 각각 반올림된 값이라 작은 차이는 허용한다.
    if abs(computed - claimed) > max(1.5, claimed * 0.05):
        return [Check(VIOLATION, PERCENT_MISMATCH, f"별표 5로 계산하면 {computed:.1f}%인데 광고는 {claimed:g}%",
                      target=target, claim_value=value, evidence=annex)]
    checks = [Check(SUPPORTED, PERCENT_CONSISTENT, f"별표 5 기준 계산값 {computed:.1f}%와 일치", target=target,
                    claim_value=value, evidence=annex)]
    found = _find_items(name, items)
    if found:
        checks.append(_compare_amount(target, amount, value, found[0], intake))
    return checks


def _check_label_percent(name: str, claimed: float, product: dict, items: list[SpecItem]) -> list[Check]:
    """함량 없이 %만 말한 경우. 표시량이 그 %와 맞으면 지지하고, 다르면 기준을 몰라 UNCLEAR다."""
    target = canonical(name)
    value = f"{claimed:g}%"
    if _is_infant(product):
        return [Check(UNCLEAR, INFANT_PRODUCT, "영유아용 제품은 별표 5 기준치를 그대로 적용하지 않음",
                      target=target, claim_value=value)]
    found = _find_items(name, items)
    reference = daily_value(name)
    if not found:
        return [Check(UNCLEAR, SPEC_NOT_FOUND, f"BASE_STANDARD에서 {target} 표시량을 찾지 못함", target=target,
                      claim_value=value)]
    item = found[0]
    if not comparable(item.amount, reference):
        return [Check(UNCLEAR, BASIS_MISMATCH, "표시량과 별표 5의 기준이 달라 계산할 수 없음", target=target,
                      claim_value=value, evidence=_spec_evidence(item))]
    computed = item.amount.base()[1] / reference.base()[1] * 100
    if abs(computed - claimed) <= max(1.5, claimed * 0.05):
        return [Check(SUPPORTED, PERCENT_MATCHES_LABEL, f"표시량 기준 계산값 {computed:.1f}%와 일치", target=target,
                      claim_value=value, evidence=_spec_evidence(item))]
    return [Check(UNCLEAR, PERCENT_NOT_CONFIRMED, f"표시량 기준 계산값 {computed:.1f}%와 다르지만 광고의 섭취 기준을 알 수 없음",
                  target=target, claim_value=value, evidence=_spec_evidence(item))]


# ---------- 함량 ----------

def _claim_amounts(claim: dict, text: str) -> list[Amount]:
    """괄호 안 병기("(40억)", "(5 g)")를 빼고 읽는다. 균수는 "12억"처럼 단위 없이도 쓴다."""
    bare = _PAREN.sub(" ", text)
    amounts = [a for a in parse_amounts(bare) if a.base()[0] in ("mass", "CFU", "IU")]
    names = " ".join(claim.get("ingredients") or []) + " " + text
    if not amounts and _MICROBE.search(names):
        amounts = [Amount(scaled_number(m["num"], None, m["large"]), "CFU") for m in _LARGE_ONLY.finditer(bare)]
    return amounts


def _check_amount(claim: dict, text: str, items: list[SpecItem], intake: Intake | None,
                  aliases: dict[str, str]) -> list[Check]:
    amounts = _claim_amounts(claim, text)
    if not amounts:
        return []
    ingredients = claim.get("ingredients") or []
    found = _claim_items(claim, text, items, amounts, aliases)
    if not found:
        if not ingredients:
            return []
        return [Check(UNCLEAR, SPEC_NOT_FOUND, "BASE_STANDARD에서 이 성분의 표시량을 찾지 못함",
                      target=", ".join(ingredients), claim_value=_show(amounts[0]))]
    if len(amounts) != 1 or len(found) != 1:
        return [Check(UNCLEAR, MULTIPLE_VALUES, "수치나 성분이 여러 개라 어떤 값끼리 비교할지 정할 수 없음",
                      target=", ".join(i.name for i in found), claim_value=", ".join(_show(a) for a in amounts))]
    return [_compare_amount(found[0].name, amounts[0], _show(amounts[0]), found[0], intake)]


def _show(amount: Amount) -> str:
    value = f"{amount.value:,.0f}" if amount.value >= 1e6 else f"{amount.value:g}"
    return f"{value} {amount.unit}" + (f" {amount.basis}" if amount.basis else "")


def _compare_amount(target: str, amount: Amount, value: str, item: SpecItem, intake: Intake | None) -> Check:
    evidence = _spec_evidence(item)
    amount = _vitamin_d_mass(amount, item)
    if not comparable(amount, item.amount):
        return Check(UNCLEAR, BASIS_MISMATCH, "광고 단위와 표시량 단위가 달라 비교할 수 없음", target=target,
                     claim_value=value, evidence=evidence)
    if same_amount(amount, item.amount):
        return Check(SUPPORTED, AMOUNT_MATCHES_LABEL, "표시량과 일치", target=target, claim_value=value, evidence=evidence)
    daily = daily_amount(item, intake)
    if daily is not None:
        evidence.append({"field": "SRV_USE", "value": f"하루 함량 계산값 {daily.value:g} {daily.unit}"})
        if same_amount(amount, daily):
            return Check(SUPPORTED, AMOUNT_MATCHES_DAILY, "하루 함량 계산값과 일치", target=target, claim_value=value,
                         evidence=evidence)
    # 균수 규격은 "표시량 이상"인 최솟값이고, 분모 1 g·100 g은 농도라 1회분 표시량이 아니다.
    if amount.unit == "CFU" or item.per.value in CONCENTRATION_PER or intake is None:
        return Check(UNCLEAR, BASIS_MISMATCH, "표시량과 다르지만 광고 수치가 어떤 기준량인지 알 수 없어 맞는지 판단할 수 없음", target=target,
                     claim_value=value, evidence=evidence)
    evidence.append({"field": "SRV_USE", "value": _srv_summary(intake)})
    if any(same_amount(amount, Amount(item.amount.value * f, item.amount.unit)) for f in _serving_factors(intake)):
        return Check(SUPPORTED, AMOUNT_MATCHES_SERVING, "표시량을 섭취 횟수·개수로 환산한 값과 일치", target=target,
                     claim_value=value, evidence=evidence)
    return Check(VIOLATION, AMOUNT_MISMATCH, "표시량과 섭취 횟수·개수로 환산한 값 어디에도 맞지 않음", target=target,
                 claim_value=value, evidence=evidence)


def _vitamin_d_mass(amount: Amount, item: SpecItem) -> Amount:
    if amount.unit == "IU" and canonical(item.name) == "비타민D" and item.amount.base()[0] == "mass":
        return Amount(amount.value / IU_PER_UG_VITAMIN_D, "μg")
    return amount


def _serving_factors(intake: Intake) -> set[float]:
    """표시량 분모가 1개·1회·하루 중 무엇인지 모르므로 가능한 배수를 모두 본다."""
    times, count = intake.times_per_day or 1, intake.count_per_time or 1
    return {1, times, count, times * count, 1 / times, 1 / count, 1 / (times * count), times / count, count / times}


def _srv_summary(intake: Intake) -> str:
    return f"1일 {intake.times_per_day}회, 1회 {intake.count_per_time:g}{intake.count_unit}" if intake.count_per_time \
        else f"1일 {intake.times_per_day}회"


# ---------- 섭취량 ----------

def _check_intake(text: str, intake: Intake | None, db: dict) -> list[Check]:
    claimed = parse_intake(_DAILY_WORDS.sub("1일 ", _KOREAN_COUNT.sub(_to_digit, text)))
    if claimed is None:
        return []
    evidence = [{"field": "SRV_USE", "value": db["SRV_USE"]}]
    if intake is None:
        return [Check(UNCLEAR, INTAKE_NOT_FOUND, "SRV_USE에서 섭취 횟수·개수를 읽지 못함", claim_value=text, evidence=evidence)]
    if claimed.count_per_time is None:
        ok = claimed.times_per_day == intake.times_per_day
        detail = f"1일 {claimed.times_per_day}회"
    else:
        if not _same_unit(claimed.count_unit, intake.count_unit):
            return [Check(UNCLEAR, INTAKE_UNIT_DIFFERS, f"광고 단위({claimed.count_unit})와 근거 단위({intake.count_unit})가 달라 비교할 수 없음",
                          claim_value=text, evidence=evidence)]
        ok = claimed.daily_count == intake.daily_count
        detail = f"하루 {claimed.daily_count:g}{claimed.count_unit}"
    if ok:
        return [Check(SUPPORTED, INTAKE_MATCHES, "섭취 방법과 일치", claim_value=detail, evidence=evidence)]
    return [Check(VIOLATION, INTAKE_MISMATCH, "섭취 방법과 다름", claim_value=detail, evidence=evidence)]


def _to_digit(m: re.Match) -> str:
    return f"{_KOREAN_NUMBER[m[1]]}{'회' if m[2] == '번' else m[2]}"


def _same_unit(a: str | None, b: str | None) -> bool:
    if a is None or b is None:
        return False
    if a == b or {a, b} == {"포", "스틱"}:
        return True
    return (a == _GENERIC_PILL and b in _PILLS) or (b == _GENERIC_PILL and a in _PILLS)


# ---------- 소비기한 ----------

def _months(text: str) -> int | None:
    m = _MONTHS.search(text)
    if m is None:
        return None
    return int(m[1]) * (12 if m[2] == "년" else 1)


def _check_shelf_life(text: str, db: dict) -> list[Check]:
    claimed, actual = _months(text), _months(normalize_text(db["DISTB_PD"]))
    evidence = [{"field": "DISTB_PD", "value": db["DISTB_PD"]}]
    if claimed is None or actual is None:
        return [Check(UNCLEAR, SHELF_LIFE_NOT_COMPARABLE, "날짜 표기라 제조일 기준 소비기한과 비교할 수 없음", claim_value=text,
                      evidence=evidence)]
    if claimed == actual:
        return [Check(SUPPORTED, SHELF_LIFE_MATCHES, "소비기한과 일치", claim_value=f"{claimed}개월", evidence=evidence)]
    return [Check(VIOLATION, SHELF_LIFE_MISMATCH, f"근거는 {actual}개월", claim_value=f"{claimed}개월", evidence=evidence)]


# ---------- 업력 ----------

def _check_heritage(text: str, product: dict, db: dict) -> list[Check]:
    """제조사를 직접 말하면 UNCLEAR, 아니면 OUT_OF_SCOPE다. 인허가일은 그 영업허가 시점이라 업력을 증명하지 못한다."""
    company = normalize_company(product["match"].get("matched_company"))
    if not company or company not in normalize_company(text):
        return [Check(OUT_OF_SCOPE, HERITAGE_NOT_MANUFACTURER, "제조사의 업력 주장인지 확인할 수 없음", claim_value=text)]
    years = int(_HERITAGE.search(text)[1])
    evidence = [{"field": "BSSH_PRMS_DT", "value": db["BSSH_PRMS_DT"]}]
    return [Check(UNCLEAR, HERITAGE_NOT_CONFIRMED, "인허가일은 회사 설립일이 아닐 수 있어 업력을 확인할 수 없음",
                  claim_value=f"{years}년", evidence=evidence)]
