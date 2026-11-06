"""COMPOSITION 판정. ingredients의 원료마다 제품 원재료와 대조한다.

    제품 원재료에 있음(정확, 이명, 원료명의 일부)   SUPPORTED
    알레르기 표시, 상위 범주, 상표·수식 표현        UNCLEAR (제품 사실이지만 근거로 확인 못 함)
    원료는 있지만 원산지·연근·수식 표현이 붙음      원료는 SUPPORTED, 그 표현은 UNCLEAR(문장은 UNCLEAR)
    사전에 있는 구체적인 원료인데 제품에 없음       VIOLATION
    그 외                                           UNCLEAR

제품 안의 이명은 사전에서 한 원료에만 걸릴 때만 믿는다.
없는 원료의 예외는 셋이다. 단백질·지방 같은 일반 영양소는 어떤 원료에든 들어 있을 수 있고,
"유산균혼합분말"처럼 혼합 원료가 있으면 비타민·미네랄 외의 내용물은 알 수 없으며,
"옥수수로 만든 비타민C"처럼 원료의 출처를 말하면 제품 원재료 대조 대상이 아니다. 모두 UNCLEAR다.
이름만 적힌 "혼합제제"는 예외로 두지 않는다(사용자 결정). 그 안에 있어도 없는 원료로 판정한다.
"""

import re

from ...finding import SUPPORTED, UNCLEAR, VIOLATION
from ..parsing.lexicon import Lexicon, ingredient_key, split_ingredients
from ..parsing.nutrients import canonical, part_names
from ..parsing.spec import parse_spec
from ..parsing.units import normalize_text
from ..result import Check

INGREDIENT_FOUND = "INGREDIENT_FOUND"
INGREDIENT_ALIAS = "INGREDIENT_ALIAS"
INGREDIENT_PART = "INGREDIENT_PART"
INGREDIENT_ABSENT = "INGREDIENT_ABSENT"
INGREDIENT_UNMATCHED = "INGREDIENT_UNMATCHED"
CONSTITUENT_POSSIBLE = "CONSTITUENT_POSSIBLE"
RAW_SOURCE = "RAW_SOURCE"
ALLERGEN_NOTICE = "ALLERGEN_NOTICE"
CATEGORY_TERM = "CATEGORY_TERM"
BRAND_OR_MODIFIER = "BRAND_OR_MODIFIER"
NO_INGREDIENT_SLOT = "NO_INGREDIENT_SLOT"
FORM_MATCHES = "FORM_MATCHES"
FORM_NOT_CONFIRMED = "FORM_NOT_CONFIRMED"

NAME_FIELDS = ("RAWMTRL_NM", "INDIV_RAWMTRL_NM", "ETC_RAWMTRL_NM", "CAP_RAWMTRL_NM", "PRDLST_CDNM")

_INNER = re.compile(r"\(([^()]*)\)")
_ALLERGEN_WORD = re.compile(r"알레르기|알러지")
ALLERGENS = {"우유", "대두", "쇠고기", "돼지고기", "닭고기", "계란", "난류", "땅콩", "밀", "메밀", "호두", "새우", "게", "오징어", "고등어",
             "조개류", "복숭아", "토마토", "잣", "아황산류"}
_CATEGORY = re.compile(r"^(?:멀티)?비타민|미네랄|영양소|복합균주|\d+\s*(?:종|가지|속)|^vitamins$|^minerals$", re.IGNORECASE)
_NUTRIENT_NAME = re.compile(r"^비타민\s*[a-kA-K]\d*$")
_BRAND = re.compile(r"[™®]|[A-Za-z]+-?\d+[A-Za-z]*|[a-z][A-Z]")
_LATIN_NAME = re.compile(r"^[A-Za-z .-]+$")
_VITAMIN_LETTER = re.compile(r"^[A-Ka-k]\d*$")
FORMS = {"장용성", "캡슐", "연질캡슐", "경질캡슐", "정제", "분말", "액상", "젤리", "과립", "환"}

# 광고에서 흔히 쓰는 이름 → 제품 원재료 키. 제품 자체의 이명 사전에 없어서 직접 둔다.
COMMON_NAMES = {"오메가3": "epa및dha함유유지", "유산균": "프로바이오틱스", "lutein": "루테인", "zeaxanthin": "지아잔틴",
                "astaxanthin": "아스타잔틴", "돼지감자": "뚱딴지", "피쉬콜라겐": "생선콜라겐", "굴": "굴추출물"}
_MIN_PART = 2
_SOURCE_WORD = re.compile(r"수확|재배|유래")
# 원료가 있어도 확인할 수 없는 원료 출처·수식 표현. "엽산"·"판토텐산"과 섞이지 않게 원산지는 나라 이름만 본다.
_COUNTRY = (r"국|한국|미국|독일|스위스|영국|프랑스|일본|호주|뉴질랜드|캐나다|노르웨이|칠레|페루|이탈리아|스페인|덴마크|"
            r"중국|인도|베트남|태국|브라질|아일랜드|핀란드|스웨덴|네덜란드|벨기에|그리스")
_ORIGIN = re.compile(rf"(?<![가-힣])(?:{_COUNTRY})\s*산(?![가-힣])|\d+\s*년근|수확|재배|유래|청정|원산지|산지")
# "비타민D 일명 햇살비타민" 같은 별칭은 사실 주장이 아니라 넣지 않는다.
_MODIFIER = re.compile(r"동일\s*구조|장용성|\brtg\b|알티지|고순도|순도\s*\d", re.IGNORECASE)
_MIXTURE = re.compile(r"혼합분말|혼합물|복합물")
_MACRONUTRIENTS = {"탄수화물", "당류", "식이섬유", "단백질", "지방", "포화지방", "콜레스테롤", "나트륨"}


def make_check_composition(lexicon: Lexicon):
    def check(claim: dict, product: dict) -> list[Check]:
        ingredients = claim.get("ingredients") or []
        if not ingredients:
            return [Check(UNCLEAR, NO_INGREDIENT_SLOT, "클레임에서 원료명을 찾지 못해 대조할 수 없음", claim_value=claim["text"])]
        db = product["DB"]["COMPOSITION"]
        terms = _product_terms(db)
        aliases = _product_aliases(db, lexicon)
        text = normalize_text(claim["text"])
        checks = [_check_one(name, text, db, terms, aliases, lexicon) for name in _restore_vitamins(ingredients)]
        return checks + _unverified_words(text, checks)
    return check


def _restore_vitamins(ingredients: list[str]) -> list[str]:
    """"비타민D, E"의 E처럼 비타민 바로 뒤에 글자만 오면 비타민을 붙인다."""
    out = []
    for name in ingredients:
        previous = canonical(out[-1]) if out else None
        if previous and previous.startswith("비타민") and _VITAMIN_LETTER.match(normalize_text(name).strip()):
            name = f"비타민{normalize_text(name).strip()}"
        out.append(name)
    return out


def _check_one(name: str, text: str, db: dict, terms: dict[str, tuple[str, str]], aliases: dict[str, tuple[str, str]],
               lexicon: Lexicon) -> Check:
    keys = _name_keys(name)
    plain = normalize_text(name).strip()
    if keys & FORMS or plain in FORMS:
        return _check_form(plain, db)
    if _ALLERGEN_WORD.search(text) or plain in ALLERGENS and "함유" in text:
        return Check(UNCLEAR, ALLERGEN_NOTICE, "알레르기 표시 항목은 원재료명과 일치한다고 확인할 수 없음", target=plain, claim_value=plain)
    outer = ingredient_key(_INNER.sub("", normalize_text(name)))
    if outer in terms:
        return _found(INGREDIENT_FOUND, plain, terms[outer])
    # "rTG오메가3(EPA 및 DHA 함유 유지)"는 괄호 안이 맞아도 바깥의 수식까지 확인한 것이 아니다.
    if outer and _is_more_specific({outer}, terms):
        return Check(UNCLEAR, BRAND_OR_MODIFIER, "상표·수식 표현은 원재료 필드로 확인할 수 없음", target=plain, claim_value=plain)
    for key in keys:
        if key in terms:
            return _found(INGREDIENT_FOUND, plain, terms[key])
    for key in keys:
        common = COMMON_NAMES.get(key)
        term = terms.get(common) or _containing_term(common, terms) if common else None
        if term is not None:
            return _found(INGREDIENT_ALIAS, plain, term)
    for key in keys:
        if key in aliases:
            return _found(INGREDIENT_ALIAS, plain, aliases[key])
    if _is_category(plain):
        return Check(UNCLEAR, CATEGORY_TERM, "상위 범주라 어떤 원료를 말하는지 특정할 수 없음", target=plain, claim_value=plain)
    for key in keys:
        part = _containing_term(key, terms)
        if part is not None:
            return _found(INGREDIENT_PART, plain, part)
    for other in part_names(name):
        part = _containing_term(other, terms)
        if part is not None:
            return _found(INGREDIENT_PART, plain, part)
    if _is_more_specific(keys, terms) or (_BRAND.search(plain) and not canonical(name)):
        return Check(UNCLEAR, BRAND_OR_MODIFIER, "상표·수식 표현은 원재료 필드로 확인할 수 없음", target=plain, claim_value=plain)
    fields = [{"field": f, "value": db[f]} for f in NAME_FIELDS if db[f]]
    nutrient = canonical(name)
    if nutrient or lexicon.is_representative(name):
        if _SOURCE_WORD.search(text) or re.search(re.escape(plain) + r"\s*(?:으로|로)\s*만든", text):
            return Check(UNCLEAR, RAW_SOURCE, "원료의 출처를 말하는 문장이라 제품 원재료로 확인할 수 없음", target=plain, claim_value=plain,
                         evidence=fields)
        hidden = nutrient in _MACRONUTRIENTS or (not nutrient and any(_MIXTURE.search(db[f]) for f in NAME_FIELDS))
        if hidden:
            return Check(UNCLEAR, CONSTITUENT_POSSIBLE, "원재료 필드에 없지만 다른 원료의 구성성분일 수 있어 없다고 단정할 수 없음",
                         target=plain, claim_value=plain, evidence=fields)
        return Check(VIOLATION, INGREDIENT_ABSENT, "광고한 원료가 제품 원재료 목록에 없음", target=plain, claim_value=plain,
                     evidence=fields)
    return Check(UNCLEAR, INGREDIENT_UNMATCHED, "원재료 필드와 원료 사전에서 찾지 못해 포함 여부를 판단할 수 없음", target=plain,
                 claim_value=plain)


def _found(code: str, name: str, term: tuple[str, str]) -> Check:
    return Check(SUPPORTED, code, "제품 원재료에서 확인", target=name, claim_value=name,
                 evidence=[{"field": term[0], "value": term[1]}])


def _check_form(name: str, db: dict) -> Check:
    evidence = [{"field": "SUNGSANG", "value": db["SUNGSANG"]}]
    if name and name in normalize_text(db["SUNGSANG"]):
        return Check(SUPPORTED, FORM_MATCHES, "성상과 일치", target=name, claim_value=name, evidence=evidence)
    return Check(UNCLEAR, FORM_NOT_CONFIRMED, "성상에서 해당 제형을 확인하지 못함", target=name, claim_value=name, evidence=evidence)


def _name_keys(name: str) -> set[str]:
    """비교 키: 전체, 괄호를 뺀 이름, 괄호 안 이름. "밀크씨슬(카르두스) 추출물" → "밀크씨슬추출물"도 찾는다."""
    text = normalize_text(name)
    names = [text, _INNER.sub("", text)]
    for inner in _INNER.findall(text):
        names.extend(inner.replace("또는", "").split(","))
    return {k for k in map(ingredient_key, names) if k}


def _product_terms(db: dict) -> dict[str, tuple[str, str]]:
    """{비교 키: (필드, 원문)}. 앞 필드가 우선한다."""
    terms = {}
    for field in NAME_FIELDS:
        for token in split_ingredients(db[field]):
            for key in _name_keys(token):
                terms.setdefault(key, (field, token))
    for item in parse_spec(db["BASE_STANDARD"]):
        for key in _name_keys(item.name):
            terms.setdefault(key, ("BASE_STANDARD", item.line))
    return terms


def _product_aliases(db: dict, lexicon: Lexicon) -> dict[str, tuple[str, str]]:
    """제품의 RAWMTRL_DICT_INFO 이름. 여러 원료에 걸리는 한글 이명은 쓰지 않는다. 학명은 그 제품의 값을 믿는다."""
    aliases = {}
    for entry in db["RAWMTRL_DICT_INFO"]:
        for name in [entry["ENG_NM"], entry["SCNM"], *split_ingredients(entry["RAWMTRL_NCKNM"])]:
            key = ingredient_key(name)
            if key and (lexicon.is_specific(name) or _LATIN_NAME.match(normalize_text(name).strip())):
                aliases.setdefault(key, ("RAWMTRL_DICT_INFO", entry["RPRSNT_RAWMTRL_NM"]))
    return aliases


def _is_category(name: str) -> bool:
    return bool(_CATEGORY.search(name)) and not _NUTRIENT_NAME.match(name)


def _containing_term(key: str, terms: dict[str, tuple[str, str]]) -> tuple[str, str] | None:
    """광고 이름이 제품 원료명의 일부인가("홍삼" ⊂ "홍삼농축액"). "비타민B1"은 "비타민B12"에 걸리지 않는다."""
    if len(key) < _MIN_PART:
        return None
    # "유산균발효굴추출물"의 유산균은 발효에 쓴 균이라 제품에 들었다는 근거가 아니다.
    pattern = re.compile(re.escape(key) + (r"(?!\d)" if key[-1].isdigit() else "") + "(?!발효)")
    for term, source in terms.items():
        if pattern.search(term):
            return source
    return None


def _is_more_specific(keys: set[str], terms: dict[str, tuple[str, str]]) -> bool:
    """광고 이름이 제품 원료명에 말을 덧붙인 경우("6년근 홍삼", "rTG 오메가3")."""
    known = {k for k in terms if len(k) >= _MIN_PART} | {k for k, v in COMMON_NAMES.items() if v in terms}
    return any(term != key and term in key for key in keys for term in known)


def _unverified_words(text: str, checks: list[Check]) -> list[Check]:
    """원료가 확인돼도 원산지·연근·수식 표현까지 확인한 것은 아니다. 문장 전체를 SUPPORTED로 두지 않는다."""
    if not any(c.status == SUPPORTED for c in checks):
        return []
    out = []
    origin = _ORIGIN.search(text)
    if origin:
        out.append(Check(UNCLEAR, RAW_SOURCE, "원산지·연근·원료 출처는 식약처 제품 정보로 확인할 수 없음", target=origin[0],
                         claim_value=origin[0]))
    modifier = _MODIFIER.search(text)
    if modifier:
        out.append(Check(UNCLEAR, BRAND_OR_MODIFIER, "상표·수식 표현은 원재료 필드로 확인할 수 없음", target=modifier[0],
                         claim_value=modifier[0]))
    return out
