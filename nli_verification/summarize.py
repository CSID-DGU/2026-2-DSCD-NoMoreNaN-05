"""
NLI 결과(verify.py 출력)에 최종 라벨을 붙이고, 발표용 요약을 만든다.

실행:  python summarize.py nli_results.json nli_verdicts.json
       python summarize.py nli_results.json nli_verdicts.json --require-effect   # effect가 비어 있는 Claim 제외
결과:  nli_verdicts.json (Claim별 최종 라벨)  +  nli_verdicts_report.md (발표용 표)

최종 라벨 (팀 공통 정의)
  VIOLATION     위반        질병·의약품 표현(같은 뜻 문장 3개 모두 일치) / 같은 대상을 말하는 주의사항과 반대되는 말 (C ≥ 0.9)
  OVERCLAIM     과장 주의   식약처 → 광고는 같은 말이 아니지만(E < 0.9), 광고 → 식약처는 같은 말(E ≥ 0.9)
                            + 인정 문구보다 더 말하는 신호(수치·기간, 확실성, 측정 결과 등)가 있음
                            = 인정 기능성과 같은 효능을 더 많이 말함 (run_overclaim.py로 반대 방향 계산 후)
                            과장 표현("확실히" 등)은 라벨에 쓰지 않고 '과장_표현' 칸에 참고로만 표시
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
    "DISEASE_CLAIM": "질병 예방·치료 효과를 말함 (질병 표현 문장 3개 모두 일치)",
    "DRUG_CLAIM": "의약품을 대신하거나 약효를 높인다고 말함 (의약품 표현 문장 3개 모두 일치)",
    "PRECAUTION_CONFLICT": "식약처 주의사항과 반대되는 내용",
    "MULTI_EFFECT": "여러 효능을 한 문장에 담음 (효능별로 나눠서 확인 필요)",
    "SAME_TOPIC": "인정 기능성과 같은 주제지만 같은 말인지 확인 필요 (광고 → 식약처만 성립)",
    "TRIAL_RESULT": "시험·측정 결과를 말함 (인정 범위 안인지 문구만으로 확인 어려움)",
    "IMPLIES_RECOGNIZED": "광고가 인정 기능성을 포함하고 더 말하는 내용이 없음 (광고 → 식약처 성립)",
    "EXAGGERATION_NO_EVIDENCE": "인정 근거가 없는 효과·기간·크기를 과장 표현으로 말함",
    "PART_SAME_TOPIC": "나눈 효능 중 일부가 인정 기능성과 같은 주제지만 같은 말인지 확인 필요",
    "ALL_PARTS_SUPPORTED": "여러 효능을 나눠 비교한 결과 모두 인정 기능성과 같은 내용",
    "PART_STRONGER_THAN_RECOGNIZED": "나눈 효능 중 일부가 인정 범위보다 크게 말함",
    "PART_NO_MATCHING_EVIDENCE": "나눈 효능 중 일부가 인정 기능성에 없음",
    "PART_LOW_CONFIDENCE": "나눈 효능 중 일부의 판단이 애매함",
    "STRONGER_THAN_RECOGNIZED": "인정 기능성과 같은 효능을 인정 범위보다 크게 말함 (광고 → 식약처 방향 E ≥ 0.9)",
    "NO_MATCHING_EVIDENCE": "식약처 인정 기능성 중 같은 내용이 없음",
    "LOW_CONFIDENCE": "모델 판단이 애매함",
    "QUESTION": "질문 문장이라 주장으로 보기 어려움",
    "DISEASE_DRUG_UNCERTAIN": "질병·의약품 표현일 가능성 (표현 문장 3개 중 2개 일치)",
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
            "is_health_claim": (not dis) and (bool(verify.EFFECT_WORDS.search(text)) or bool(EXTRA_CLAIM.search(text))
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


# 광고가 인정 문구보다 '더 많이' 말한다는 신호: 수치·기간, 정도·확실성, 측정 결과, 체험 결과
EXTRA_CLAIM = re.compile(r"(\d+\s*(%|배|kg)|\d+\s*(일|주|개월|달|시간|분)\s*(만에|이면|안에|째|후)|(한|두|세|네|다섯|열)\s*배|"
                         r"일주일|하루\s*만에|한\s*번만|한\s*달\s*만에|깨끗이|확실|완전|탁월|최고|싹|즉시|근본|획기|"
                         r"극대|최대|강력|절반)")
# 시험·측정 결과를 말하는 문장 (인정 범위 안인지 문구만으로 알 수 없어 판단 보류)
TRIAL_RESULT = re.compile(r"(인체\s*적용\s*시험|시험\s*결과|임상|대조군|VAS|WOMAC|MRS|평가\s*지수|유의(적|하게)|"
                          r"(증가|감소|개선)\s*확인|\d+\s*배\s*증가|CBT-|생존력|생착)")
# 주의사항 대상이 먹어도 된다고 말함 ("수유부도 먹을 수 있다")
GROUP_EAT = re.compile(r"(임산부|임신부|수유부|영\s*·?\s*유아|어린이|노약자|환자)\s*(도|까지)\s*(먹|드|섭취|복용|안심)")
DRUG_WORDS = re.compile(r"(약|치료제|주사|의약품)\s*(을|를)?\s*(대신|대체)|대신\s*(먹|드시)|끊어도")
DISEASE_WORDS = re.compile(r"치료(한다|합니다|해\s*준|해준|해요|됩니다|효과)|완치|항암|낫게|병을\s*고|환자의|생약\s*복합제")
MULTI_EFFECT = re.compile(r"[·&＆]|\s및\s|\s과\s|\s와\s|동시에|더블\s*케어")


def _groups(text):
    return {g for g, pat in GROUPS.items() if re.search(pat, text or "")}


def _precaution_conflict(c):
    """C ≥ 0.9인 주의사항 중, 광고와 같은 대상·상황을 말하는 것이 있으면 그 문장을 돌려줌.
    광고가 "수유부도 먹을 수 있다"처럼 주의 대상이 먹어도 된다고 하면, 같은 대상을 말하는 주의사항만 있어도 충돌"""
    if GROUP_EAT.search(c.get("text") or ""):
        g0 = _groups(c.get("text"))
        for x in c.get("checks") or []:
            if x.get("evidence_type") == "PRECAUTION" and g0 & _groups(x.get("premise")):
                return x.get("premise")
    cand = [x for x in (c.get("checks") or []) if x.get("evidence_type") == "PRECAUTION" and x.get("C", 0) >= TAU_HIGH]
    if not cand and (c.get("max_contra_precaution") or 0) >= TAU_HIGH:      # checks가 없을 때 (판정 파일만 있을 때)
        cand = [{"premise": c.get("best_precaution_text"), "C": c.get("max_contra_precaution")}]
    g = _groups(c.get("text"))
    for x in sorted(cand, key=lambda x: -x["C"]):
        if g & _groups(x.get("premise")):
            return x.get("premise")
    return None


def c_flags_exag(c):
    try:
        import verify
        return bool(verify.EXAGGERATION.search(c.get("text") or ""))
    except ImportError:
        return False


def _split_ok(text):
    """효능별 나누기를 믿을 수 있는 경우: '·', '&', '/', '○○건강과' 로 이어졌거나, 식약처식 나열("…에 도움을 줄 수 있음")
    쉼표만으로 이어진 일반 문장("하루 종일 스마트폰, 컴퓨터, TV에…")은 나눈 결과를 쓰지 않음"""
    t = text or ""
    return bool(re.search(r"[·&＆/]|건강\s*(과|와)", t) or re.search(r"도움을\s*줄\s*수|에\s*필요", t))


TMPL_NAMES = {"1호 가 (질병 예방)": "질병 예방", "1호 나 (질병 치료)": "질병 치료",
              "2호 다 (의약품 대체)": "의약품 대체", "2호 라 (약효 증대)": "의약품 효능 증대"}


def _tmpl_name(name):
    """예전 결과 파일의 템플릿 이름도 지금 이름(질병 예방 등)으로 읽음"""
    return TMPL_NAMES.get(name, name)


def _part_label(pt):
    """나눈 부분 하나의 판정: (라벨, 코드, 근거)"""
    e, r = pt.get("max_E"), pt.get("reverse_E") or 0
    if e is not None and e >= TAU_HIGH:
        return ("SUPPORTED", "FUNCTION", pt.get("best_text"))
    if r >= TAU_HIGH:
        if EXTRA_CLAIM.search(pt.get("text") or ""):
            return ("OVERCLAIM", "STRONGER_THAN_RECOGNIZED", pt.get("reverse_best_text"))
        return ("SUPPORTED", "IMPLIES_RECOGNIZED", pt.get("reverse_best_text"))
    if e is not None and e <= TAU_LOW:
        return ("UNCLEAR", "NO_MATCHING_EVIDENCE", None)
    return ("UNCLEAR", "LOW_CONFIDENCE", pt.get("best_text"))


def findings_of(c):
    """Claim 하나의 검사 결과를 (라벨, 코드, 근거 문장) 목록으로 만든다"""
    c = _recompute_flags(c)
    out = []
    e, cc = c.get("max_entail_function"), c.get("max_contra_precaution")
    has_ev = c.get("basis") != "NONE"
    if c.get("is_disclaimer"):
        return [("DISCLAIMER", "DISCLAIMER", None)]      # 팀 기준: 면책 문구는 별도 라벨

    # 질병·의약품 표현 (같은 뜻 문장 3개로 확인)
    supported = has_ev and e is not None and e >= TAU_HIGH
    for name, t in (c.get("templates") or {}).items():
        kind = _tmpl_name(name)
        if supported and kind == "질병 예방":
            continue    # 인정 기능성과 같은 뜻이면(예: "면역력") 질병 예방 표현으로 보지 않음
        code = "DISEASE_CLAIM" if kind.startswith("질병") else "DRUG_CLAIM"
        name = kind
        if t.get("status") == "HOLDS":
            out.append(("VIOLATION", code, name))
        elif t.get("status") == "UNCLEAR":
            out.append(("UNCLEAR", "DISEASE_DRUG_UNCERTAIN", name))

    # 질병·의약품 표현을 직접 말하는 단어 ("고혈압약을 대신할 수 있다", "관절염을 치료한다")
    text_ = c.get("text") or ""
    if not c.get("is_question"):
        if DRUG_WORDS.search(text_):
            out.append(("VIOLATION", "DRUG_CLAIM", DRUG_WORDS.search(text_).group(0)))
        elif DISEASE_WORDS.search(text_) and not supported:
            out.append(("VIOLATION", "DISEASE_CLAIM", DISEASE_WORDS.search(text_).group(0)))

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
        elif TRIAL_RESULT.search(c.get("text") or ""):
            out.append(("UNCLEAR", "TRIAL_RESULT", c.get("reverse_best_text")))
        elif e is not None and e <= TAU_LOW and EXTRA_CLAIM.search(c.get("text") or ""):
            out.append(("OVERCLAIM", "EXAGGERATION_NO_EVIDENCE", None))
        elif c.get("parts") and _split_ok(c.get("text")):
            # 여러 효능을 한 문장에 담은 클레임: 효능별로 나눠 판정한 뒤 합침
            plabs = [_part_label(pt) for pt in c["parts"]]
            worst = min(plabs, key=lambda x: ORDER.index(x[0]))
            if all(x[0] == "SUPPORTED" for x in plabs):
                out.append(("SUPPORTED", "ALL_PARTS_SUPPORTED", " / ".join(x[2] or "" for x in plabs)))
            else:
                out.append((worst[0], "PART_" + worst[1], worst[2]))
        elif (c.get("reverse_max_E") or 0) >= TAU_HIGH and MULTI_EFFECT.search(c.get("text") or ""):
            # 효능 여러 개를 한 문장에 담으면 반대 방향은 성립하지만 과장이 아닐 수 있음 (예: "혈행·혈중 중성지질 개선")
            out.append(("UNCLEAR", "MULTI_EFFECT", c.get("reverse_best_text")))
        elif (c.get("reverse_max_E") or 0) >= TAU_HIGH:
            # 반대 방향(광고 → 식약처)만 성립: 광고가 인정 기능성과 같은 주제를 말함
            #   + 인정 문구보다 더 말하는 신호(수치·기간·확실성·측정 결과 등)가 있으면 → OVERCLAIM
            #   + 신호가 없으면 같은 말을 다르게 표현했거나(모델이 정방향을 놓침) 막연한 표현 → UNCLEAR
            if EXTRA_CLAIM.search(c.get("text") or ""):
                out.append(("OVERCLAIM", "STRONGER_THAN_RECOGNIZED", c.get("reverse_best_text")))
            else:
                out.append(("SUPPORTED", "IMPLIES_RECOGNIZED", c.get("reverse_best_text")))
        elif e is not None and e <= TAU_LOW:
            if EXTRA_CLAIM.search(c.get("text") or "") or c_flags_exag(c):
                out.append(("OVERCLAIM", "EXAGGERATION_NO_EVIDENCE", None))
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
                "부분별_결과": [{"부분": pt.get("text"), "라벨": _part_label(pt)[0],
                                 "식약처→광고_E": pt.get("max_E"), "광고→식약처_E": pt.get("reverse_E"),
                                 "근거": _part_label(pt)[2]} for pt in (c.get("parts") or [])]
                                if c.get("parts") and _split_ok(c.get("text")) else None,
            })
    uniq = [r for r in rows if not r["중복"]]
    summary = {
        "Claim 수 (중복 제외)": len(uniq),
        "최종 라벨": {k: n for k, n in Counter(r["최종_라벨"] for r in uniq).most_common()},
        "사유 코드": {k: n for k, n in Counter(r["사유_코드"] for r in uniq).most_common()},
    }
    return {"요약": summary, "claims": rows}


def export_records(results):
    """통합·평가용 영문 형식 (클레임 1개 = 레코드 1개)"""
    recs = []
    for v in results:
        for c in v.get("nli_claims", []):
            label, code, ev, fs = final_label(c)
            f = _recompute_flags(c)
            parts = None
            if c.get("parts") and _split_ok(c.get("text")):
                parts = [{"text": p.get("text"), "label": _part_label(p)[0], "reason_code": _part_label(p)[1],
                          "E": p.get("max_E"), "reverse_E": p.get("reverse_E"), "evidence_text": _part_label(p)[2]}
                         for p in c["parts"]]
            recs.append({
                "video_id": v.get("video_id"), "product_ref": v.get("product_ref"), "claim_id": c.get("claim_id"),
                "claim_type": c.get("claim_types") or c.get("claim_type"), "text": c.get("text"), "mechanism": "B",
                "label": label, "reason_code": code, "reason": CODE_KO.get(code, code), "evidence_text": ev,
                "scores": {"E": c.get("max_entail_function"), "C": c.get("max_contra_precaution"),
                           "reverse_E": c.get("reverse_max_E"), "health_claim_E": c.get("health_claim_E")},
                "all_findings": [{"label": a, "reason_code": b} for a, b, _ in fs],
                "flags": {"is_question": bool(c.get("is_question")), "exaggeration_terms": f.get("exaggeration_terms") or []},
                "parts": parts, "duplicate_of": c.get("duplicate_of"), "product_name": v.get("product_name"),
            })
    return recs


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
    eng = dst.replace(".json", "_mechanism_b.json")
    with open(eng, "w", encoding="utf-8") as f:
        json.dump({"mechanism": "B", "target_claim_type": "EFFECT", "label_order": ORDER,
                   "thresholds": {"tau_high": TAU_HIGH, "tau_low": TAU_LOW},
                   "results": export_records(results)}, f, ensure_ascii=False, indent=2)
    print("최종 라벨:", out["요약"]["최종 라벨"])
    print("저장:", dst, "/", md, "/", eng)
