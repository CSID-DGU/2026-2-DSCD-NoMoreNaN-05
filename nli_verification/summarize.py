"""
NLI 결과(verify.py 출력)에 최종 라벨을 붙이고, 발표용 요약을 만든다.

실행:  python summarize.py nli_results.json nli_verdicts.json
       python summarize.py nli_results.json nli_verdicts.json --require-effect   # effect가 비어 있는 Claim 제외
결과:  nli_verdicts.json (Claim별 최종 라벨)  +  nli_verdicts_report.md (발표용 표)

최종 라벨 (팀 공통 정의)
  VIOLATION     위반        질병·의약품 금지 표현(템플릿 3개 모두 일치) / 같은 대상을 말하는 주의사항과 반대되는 말 (C ≥ 0.9)
  OVERCLAIM     과장 주의   인정 기능성과 같은 말이 없고(E ≤ 0.1) + 과장 표현이 있음
  UNCLEAR       판단 보류   인정 기능성과 같은 말이 없음 / 확률이 애매함 / 질문 문장 / 비교할 근거 없음
  SUPPORTED     부합        식약처 인정 기능성과 같은 말 (E ≥ 0.9)
  OUT_OF_SCOPE  해당 없음   건강 효과를 말하지 않는 문장
  DISCLAIMER    면책 문구   "인체적용시험결과가 모든 사람에게 동일하게 적용되는 것은 아님" 등

한 Claim에 여러 결과가 나오면 VIOLATION > OVERCLAIM > UNCLEAR > SUPPORTED > OUT_OF_SCOPE 순으로 대표 라벨을 정한다.
기준값 0.9 / 0.1은 임시값.
"""
import json
import re
import sys
from collections import Counter

TAU_HIGH, TAU_LOW = 0.9, 0.1
ORDER = ["VIOLATION", "OVERCLAIM", "UNCLEAR", "SUPPORTED", "OUT_OF_SCOPE", "DISCLAIMER"]
LABEL_KO = {"VIOLATION": "위반", "OVERCLAIM": "과장 주의", "UNCLEAR": "판단 보류",
            "SUPPORTED": "부합", "OUT_OF_SCOPE": "해당 없음", "DISCLAIMER": "면책 문구"}
CODE_KO = {
    "DISEASE_CLAIM": "질병 예방·치료 효과를 말함 (법 제8조 1호)",
    "DRUG_CLAIM": "의약품처럼 오인하게 함 (법 제8조 2호)",
    "PRECAUTION_CONFLICT": "식약처 주의사항과 반대되는 내용",
    "EXAGGERATION_TERM": "인정 기능성보다 효과를 크게 표현 (과장 표현 포함)",
    "NO_MATCHING_EVIDENCE": "식약처 인정 기능성 중 같은 내용이 없음",
    "LOW_CONFIDENCE": "모델 판단이 애매함",
    "QUESTION": "질문 문장이라 주장으로 보기 어려움",
    "DISEASE_DRUG_UNCERTAIN": "질병·의약품 표현일 가능성 (금지 문장 3개 중 2개 일치)",
    "PRODUCT_UNRESOLVED": "광고 제품을 식약처 DB에서 확정하지 못함",
    "NO_PRODUCT_TEXT": "제품의 기능성 문장이 없음",
    "INGREDIENT_NOT_IN_PRODUCT": "광고가 말하는 원료가 제품 기능성에 없거나 애매함",
    "TARGET_UNRESOLVED": "광고가 무엇에 대해 말하는지 알 수 없음",
    "FUNCTION": "식약처 인정 기능성과 같은 내용",
    "NOT_HEALTH_CLAIM": "건강 효과를 말하는 문장이 아님",
    "DISCLAIMER": "광고 속 면책·고지 문구 (주장이 아님)",
}


def _recompute_flags(c):
    """건강 효과 문장·면책 문구·과장 표현을 verify.py의 최신 규칙으로 다시 계산 (NLI를 다시 돌리지 않아도 됨)"""
    try:
        import verify
    except ImportError:
        return c
    text = c.get("text") or ""
    dis = bool(verify.DISCLAIMER.search(text))
    h = c.get("health_claim_E")
    e = c.get("max_entail_function")
    return {**c, "is_disclaimer": dis,
            "is_health_claim": (not dis) and (bool(verify.EFFECT_WORDS.search(text))
                                              or (h is not None and h >= verify.SCOPE_TAU)
                                              or (e is not None and e >= TAU_HIGH)),   # 인정 기능성과 같은 말이면 효능 주장
            "exaggeration_terms": sorted({m.group(0) for m in verify.EXAGGERATION.finditer(text)})}


# 주의사항 충돌은 광고와 주의사항이 같은 대상·상황을 말할 때만 인정 (관련 없는 주의사항과의 C는 NLI 오판이 많음)
GROUPS = {
    "임산부": r"임산부|임신|수유", "어린이": r"영\s*·?\s*유아|유아|어린이|소아|아이", "노약자": r"노약자|고령|노인|어르신",
    "약": r"의약품|약을|약과|약\s|약$|치료제|복용", "당뇨": r"당뇨|혈당", "혈압": r"혈압", "혈액응고": r"항응고|와파린|혈액\s*응고|출혈",
    "알레르기": r"알레르기|알러지", "수술": r"수술", "월경": r"월경|생리", "갑상선": r"갑상선", "간": r"간\s*질환|간\s*기능",
    "신장": r"신장|콩팥", "심장": r"심장|심혈관", "과량": r"과량|과다|많이\s*(먹|드)|여러\s*(알|개)|두\s*배", "음주": r"음주|술",
}


def _groups(text):
    return {g for g, pat in GROUPS.items() if re.search(pat, text or "")}


def _precaution_conflict(c):
    """C ≥ 0.9인 주의사항 중, 광고와 같은 대상·상황을 말하는 것이 있으면 그 문장을 돌려줌"""
    cand = [x for x in (c.get("checks") or []) if x.get("evidence_type") == "PRECAUTION" and x.get("C", 0) >= TAU_HIGH]
    if not cand and (c.get("max_contra_precaution") or 0) >= TAU_HIGH:      # checks가 없을 때 (판정 파일만 있을 때)
        cand = [{"premise": c.get("best_precaution_text"), "C": c.get("max_contra_precaution")}]
    g = _groups(c.get("text"))
    for x in sorted(cand, key=lambda x: -x["C"]):
        if g & _groups(x.get("premise")):
            return x.get("premise")
    return None


def findings_of(c):
    """Claim 하나의 검사 결과를 (라벨, 코드, 근거 문장) 목록으로 만든다"""
    c = _recompute_flags(c)
    out = []
    e, cc = c.get("max_entail_function"), c.get("max_contra_precaution")
    has_ev = c.get("basis") != "NONE"
    if c.get("is_disclaimer"):
        return [("DISCLAIMER", "DISCLAIMER", None)]      # 팀 기준: 면책 문구는 별도 라벨

    # 질병·의약품 금지 표현 (법 제8조 1·2호)
    supported = has_ev and e is not None and e >= TAU_HIGH
    for name, t in (c.get("templates") or {}).items():
        if supported and name.startswith("1호 가"):
            continue    # v4 예외: 인정 기능성과 같은 뜻이면(예: "면역력") 질병 예방 표현으로 보지 않음
        code = "DISEASE_CLAIM" if name.startswith("1호") else "DRUG_CLAIM"
        if t.get("status") == "HOLDS":
            out.append(("VIOLATION", code, name))
        elif t.get("status") == "UNCLEAR":
            out.append(("UNCLEAR", "DISEASE_DRUG_UNCERTAIN", name))

    # 주의사항 충돌 (건강 효과 확인보다 먼저: 안전 문제). 같은 대상·상황을 말하는 주의사항만
    if has_ev:
        prec = _precaution_conflict(c)
        if prec:
            out.append(("VIOLATION", "PRECAUTION_CONFLICT", prec))

    # 기능성 비교 (건강 효과를 말하는 문장만)
    if c.get("is_question"):
        out.append(("UNCLEAR", "QUESTION", None))
    elif c.get("is_health_claim"):
        if not has_ev:
            out.append(("UNCLEAR", c.get("basis_reason") or "TARGET_UNRESOLVED", None))
        elif e is not None and e >= TAU_HIGH:
            out.append(("SUPPORTED", "FUNCTION", c.get("best_function_text")))
        elif e is not None and e <= TAU_LOW:
            if c.get("exaggeration_terms"):
                out.append(("OVERCLAIM", "EXAGGERATION_TERM", c.get("best_function_text")))
            else:
                out.append(("UNCLEAR", "NO_MATCHING_EVIDENCE", None))
        else:
            out.append(("UNCLEAR", "LOW_CONFIDENCE", c.get("best_function_text")))

    if not out:
        out.append(("OUT_OF_SCOPE", "NOT_HEALTH_CLAIM", None))
    return out


def final_label(c):
    fs = findings_of(c)
    label = min((f[0] for f in fs), key=ORDER.index)
    main = next(f for f in fs if f[0] == label)
    return label, main[1], main[2], fs


def summarize(results, require_effect=False):
    rows = []
    for v in results:
        for c in v.get("nli_claims", []):
            if require_effect and not c.get("effect"):
                continue        # effect(효과 문구)가 비어 있는 Claim 제외 (팀 집계 기준 1,287건에 맞출 때)
            label, code, ev, fs = final_label(c)
            rows.append({
                "video_id": v.get("video_id"), "product_ref": v.get("product_ref"),
                "제품명": v.get("product_name"), "claim_id": c.get("claim_id"),
                "광고_문장": c.get("text"),
                "최종_라벨": label, "라벨_설명": LABEL_KO[label],
                "사유_코드": code, "사유": CODE_KO.get(code, code),
                "근거": ev,
                "같은_말_확률(E)": c.get("max_entail_function"),
                "반대되는_말_확률(C)": c.get("max_contra_precaution"),
                "건강_효과_문장_확률": c.get("health_claim_E"),
                "과장_표현": c.get("exaggeration_terms") or [],
                "비교_근거": c.get("basis"),
                "모든_검사_결과": [{"라벨": a, "코드": b} for a, b, _ in fs],
                "중복": c.get("duplicate_of"),
            })
    uniq = [r for r in rows if not r["중복"]]
    summary = {
        "Claim 수 (중복 제외)": len(uniq),
        "최종 라벨": {k: n for k, n in Counter(r["최종_라벨"] for r in uniq).most_common()},
        "사유 코드": {k: n for k, n in Counter(r["사유_코드"] for r in uniq).most_common()},
    }
    return {"요약": summary, "claims": rows}


def to_markdown(out, n_examples=5):
    s = out["요약"]
    lines = ["# NLI 검증 결과 요약", "", f"- Claim 수 (중복 제외): **{s['Claim 수 (중복 제외)']}**", "",
             "## 최종 라벨", "", "| 라벨 | 설명 | 개수 | 비율 |", "|---|---|---|---|"]
    total = s["Claim 수 (중복 제외)"] or 1
    for k in ORDER:
        n = s["최종 라벨"].get(k, 0)
        lines.append(f"| {k} | {LABEL_KO[k]} | {n} | {n / total:.1%} |")
    lines += ["", "## 사유 코드", "", "| 코드 | 뜻 | 개수 |", "|---|---|---|"]
    for k, n in s["사유 코드"].items():
        lines.append(f"| {k} | {CODE_KO.get(k, k)} | {n} |")
    for k in ORDER:
        ex = [r for r in out["claims"] if r["최종_라벨"] == k and not r["중복"]][:n_examples]
        if not ex:
            continue
        lines += ["", f"## 예시: {k} ({LABEL_KO[k]})", "", "| 제품 | 광고 문장 | 사유 | E | 근거 |", "|---|---|---|---|---|"]
        for r in ex:
            ev = (r["근거"] or "").replace("|", "/")
            lines.append(f"| {r['제품명']} | {r['광고_문장']} | {r['사유']} | {r['같은_말_확률(E)']} | {ev} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    require_effect = "--require-effect" in sys.argv
    src = args[0] if args else "nli_results.json"
    dst = args[1] if len(args) > 1 else src.replace(".json", "_verdicts.json")
    with open(src, "rb") as f:
        results = json.loads(f.read().decode("utf-8-sig"))
    out = summarize(results, require_effect)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    md = dst.replace(".json", "_report.md")
    with open(md, "w", encoding="utf-8") as f:
        f.write(to_markdown(out))
    print("최종 라벨:", out["요약"]["최종 라벨"])
    print("저장:", dst, "/", md)
