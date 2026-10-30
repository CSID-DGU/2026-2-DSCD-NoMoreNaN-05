"""DB `diseases`(KCD)에서 판정용 질병 사전을 만든다.

    python -m claim_verification.scripts.build_disease_terms [DB 경로]

KCD 정식 명칭("병적 골절이 없는 골다공증")은 광고 표현("골다공증")과 다르다.
그래서 정식 명칭에서 광고에 쓰일 만한 명칭만 뽑아 resources/disease_terms.json에 고정한다.
판정할 때는 이 파일만 읽고 DB는 읽지 않는다.

- 장 A~Q는 disease, R(증상·징후)은 symptom. S~Z(손상·중독·외부요인·보건서비스)와 U(한방 특수)는 뺀다.
- 양방(medicine_type 1) 명칭만 쓴다. 한방 명칭은 일반 단어와 겹쳐 오탐이 많다.
- source: core(정식 명칭의 끝 단어), whole(한 단어로 된 정식 명칭), alias(대괄호 속 별칭),
  manual(직접 보충한 광고 표현)
"""

import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data/bundle_20261007/Data_List_Claim_Verification/claim_verification.sqlite"
OUT = ROOT / "claim_verification/resources/disease_terms.json"

DISEASE, SYMPTOM = "disease", "symptom"

# 끝 단어가 이 꼴이어야 질병 명칭으로 본다. "태아", "피부", "약물" 같은 끝 단어를 거른다.
DISEASE_SUFFIX = re.compile(
    r"(증|병|염|암|종|통|압|궤양|결석|부전|경화|결핵|빈혈|치매|천식|비만|탈모|골절|변비|설사"
    r"|마비|경련|발작|중독|색전|경색|혈전|탈출|농양|낭종)$"
)
# 끝 단어 꼴은 맞지만 질병명이 아닌 말. 일반 명사이거나 인정 기능성 문구에 쓰인다.
STOP = {"증상", "합병증", "후유증", "병태", "진통", "통증", "질병", "질환", "동통", "혈압"}
# 한 단어 정식 명칭 중 일반 단어와 뜻이 겹치는 말 (주사=딸기코/주사기, 단독=단독/혼자, 복수=복수/원수)
HOMONYM = {"주사", "단독", "복수", "부동", "중첩", "원시", "사위", "보선", "혈질", "요스", "마마", "질식",
           "노쇠", "창백", "혼미", "구역", "신경질", "적대감", "불행감", "악몽", "탈수", "환시", "환청"}
# 정식 명칭 앞뒤에서 떼는 수식어
PREFIX = re.compile(r"^(상세불명의|기타|달리 분류되지 않은|달리 분류된)\s*")
SPLIT = re.compile(r",|\s및\s|\s또는\s|\s그리고\s")

# DB에 없거나 KCD가 다르게 적는 광고 표현. 암은 KCD가 "위의 악성 신생물"로 적어 "위암"이 생기지 않는다.
MANUAL = {
    "암": DISEASE, "위암": DISEASE, "간암": DISEASE, "폐암": DISEASE, "대장암": DISEASE,
    "유방암": DISEASE, "갑상선암": DISEASE, "전립선암": DISEASE, "췌장암": DISEASE,
    "자궁경부암": DISEASE, "혈액암": DISEASE,
    "당뇨": DISEASE, "고혈압": DISEASE, "탈모": DISEASE, "난임": DISEASE, "불임": DISEASE,
    "성조숙증": DISEASE, "숙취": DISEASE, "아토피": DISEASE, "동맥경화": DISEASE,
    "뇌졸중": DISEASE, "황반변성": DISEASE, "안구건조증": DISEASE, "전립선비대증": DISEASE,
    "소화불량": DISEASE, "역류성식도염": DISEASE, "다낭성난소증후군": DISEASE,
    "감기": DISEASE, "독감": DISEASE, "치매": DISEASE, "뇌경색": DISEASE, "심근경색": DISEASE,
    "잇몸질환": DISEASE, "치주질환": DISEASE, "귀울림": DISEASE,
    # KCD는 "치아우식"으로 적는다. 질병발생위험감소 인정 문구("충치발생 위험 감소")가 이 말을 쓴다.
    "충치": DISEASE,
}
# 질병명이면서 일반 단어로도 쓰이는 말. 탐지할 때 문맥을 더 본다.
AMBIGUOUS = {"통풍", "중독", "경련", "마비", "발작", "기미", "수종"}

MAX_FROM_NAMES = 5


def kind_of(code: str) -> str | None:
    chapter = code[0]
    if "A" <= chapter <= "Q":
        return DISEASE
    if chapter == "R":
        return SYMPTOM
    return None


def terms_from_name(name: str) -> list[tuple[str, str]]:
    """정식 명칭 하나에서 (명칭, source) 목록을 뽑는다."""
    # 별칭에는 "제3뇌[동안]신경", "[ALL]" 같은 주석도 섞여 있어 질병 꼴인 것만 쓴다.
    found = [(a.strip(), "alias") for a in re.findall(r"\[([^\]]+)\]", name)
             if DISEASE_SUFFIX.search(a.strip())]
    base = re.sub(r"\[.*?\]|\(.*?\)|[†*]", "", name).strip()
    if re.fullmatch(r"[가-힣]+", base) and base not in HOMONYM:
        found.append((base, "whole"))
    for part in SPLIT.split(base):
        words = PREFIX.sub("", part.strip()).split()
        if words and DISEASE_SUFFIX.search(words[-1]):
            found.append((words[-1], "core"))
    return [(t, s) for t, s in found if (len(t) >= 2 or t == "암") and t not in STOP]


def build(db_path: Path) -> dict:
    db = sqlite3.connect(db_path)
    rows = db.execute(
        "SELECT DISTINCT disease_code, disease_name FROM diseases WHERE medicine_type = '1'"
    ).fetchall()
    loaded_at = db.execute(
        "SELECT loaded_at FROM dataset_registry WHERE dataset_key = 'diseases'"
    ).fetchone()

    terms = defaultdict(lambda: {"kinds": set(), "sources": set(), "codes": set(), "from_names": []})
    for code, name in rows:
        kind = kind_of(code)
        if kind is None:
            continue
        for term, source in terms_from_name(name):
            t = terms[term]
            t["kinds"].add(kind)
            t["sources"].add(source)
            t["codes"].add(code[:3])
            if name not in t["from_names"] and len(t["from_names"]) < MAX_FROM_NAMES:
                t["from_names"].append(name)
    for term, kind in MANUAL.items():
        terms[term]["kinds"].add(kind)
        terms[term]["sources"].add("manual")

    out = []
    for term in sorted(terms):
        t = terms[term]
        out.append({
            "term": term,
            # A~Q와 R 양쪽에 있으면 질병으로 본다 (예: 두통은 G44와 R51).
            "kind": DISEASE if DISEASE in t["kinds"] else SYMPTOM,
            "sources": sorted(t["sources"]),
            "ambiguous": term in AMBIGUOUS,
            "codes": sorted(t["codes"]),
            "from_names": t["from_names"],
        })
    return {
        "meta": {"source": "diseases (KCD)", "db_loaded_at": loaded_at[0] if loaded_at else None,
                 "term_count": len(out)},
        "terms": out,
    }


def main() -> None:
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB
    result = build(db_path)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {result['meta']['term_count']}개")


if __name__ == "__main__":
    main()
