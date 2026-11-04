"""
전체 Claim 파일(claims_with_db_501_no_etc.json)로 Claim 유형별 NLI 결과를 정리한다.
제품이 DB와 확정 매핑된(DB가 있는) 제품의 Claim만 대상으로 한다.

목적: NLI(의미 비교)가 어떤 Claim 유형에 쓸모 있는지 확인
      → EFFECT는 NLI(Mechanism B), 숫자·성분·인증은 규칙·DB 비교(Mechanism A)가 맞는지 근거 만들기

실행:  python run_bytype.py claims_with_db_501_no_etc.json
결과:  bytype_nli_results.json (Claim별), bytype_report.md (유형별 요약 표)

유형별 전제(식약처 문장) 만드는 법
  EFFECT         DB.EFFECT.MAIN_FNCTN (기능성) + INTAKE_HINT1 (주의사항)
  QUANTITY       DB.QUANTITY.BASE_STANDARD의 '표시량' 줄 → "○○의 비타민C 함량은 1560 mg당 100 mg이다"
  COMPOSITION    DB.COMPOSITION.RAWMTRL_NM 원료 목록 → "○○에는 판토텐산이 들어 있다"
  CERTIFICATION  DB.CERTIFICATION → "○○은 식품의약품안전처에 신고된 건강기능식품이다" 등
  PERSON_CREDENTIAL  비교할 공식 자료 없음 → NLI 생략
"""
import argparse
import json
import re
import time
from collections import Counter, defaultdict

from evidence_prep import make_premise, parse_functionality, parse_precautions, topic_particle
from hypothesis import make_hypothesis
from nli import NLIScorer, MODEL_NAME

TAU = 0.9


def subj_particle(word):          # 이/가
    return "이" if topic_particle(word) == "은" else "가"


def premises_for(ctype, db, name):
    """유형별로 식약처 DB에서 전제 문장 목록을 만든다. 반환: [(종류, 전제 문장)]"""
    out = []
    if ctype == "EFFECT":
        e = db.get("EFFECT") or {}
        out += [("기능성", make_premise(name, r["core"])) for r in parse_functionality(e.get("MAIN_FNCTN") or "")]
        out += [("주의사항", r["core"]) for r in parse_precautions(e.get("INTAKE_HINT1") or "")]
    elif ctype == "QUANTITY":
        q = db.get("QUANTITY") or {}
        for line in (q.get("BASE_STANDARD") or "").split("\n"):
            m = re.search(r"^\s*\d+\)\s*([^:：]+)[:：]\s*표시량\s*\(\s*([^/)]+?)\s*/\s*([^)]+?)\s*\)", line)
            if m:
                ing, amt, base = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
                out.append(("표시량", f"{name}의 {ing} 함량은 {base}당 {amt}이다"))
        if q.get("SRV_USE"):
            out.append(("섭취방법", f"{name}의 섭취 방법은 다음과 같다: {q['SRV_USE'].strip()}"))
    elif ctype == "COMPOSITION":
        c = db.get("COMPOSITION") or {}
        names = [x.strip() for x in re.split(r"[,，]", c.get("RAWMTRL_NM") or "") if x.strip()]
        out += [("원료", f"{name}에는 {x}{subj_particle(x)} 들어 있다") for x in names]
        if c.get("INDIV_RAWMTRL_NM"):
            out.append(("원료", f"{name}의 기능성 원료는 {c['INDIV_RAWMTRL_NM'].strip()}이다"))
    elif ctype == "CERTIFICATION":
        c = db.get("CERTIFICATION") or {}
        out.append(("인증", f"{name}{topic_particle(name)} 식품의약품안전처에 신고된 건강기능식품이다"))
        if c.get("STTEMNT_NO"):
            out.append(("인증", f"{name}의 품목제조신고번호는 {c['STTEMNT_NO']}이다"))
        if c.get("INDUTY_CD_NM"):
            out.append(("인증", f"{name}{topic_particle(name)} {c['INDUTY_CD_NM']} 업체가 제조한다"))
    return out


def judge(best_e, best_c):
    if best_e is not None and best_e >= TAU:
        return "E (같은 말)"
    if best_c is not None and best_c >= TAU:
        return "C (반대되는 말)"
    if best_e is not None and best_e <= 0.1:
        return "N (관련 없음)"
    return "애매 (0.1~0.9)"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="claims_with_db_501_no_etc.json")
    ap.add_argument("--model", default=MODEL_NAME)
    ap.add_argument("--prefix", default="bytype", help="결과 파일 이름 앞부분")
    args = ap.parse_args()

    with open(args.input, "rb") as f:
        videos = json.loads(f.read().decode("utf-8-sig"))

    jobs, plans, skipped = [], [], Counter()
    for v in videos:
        prods = {p["product_ref"]: p for p in v.get("products", [])}
        for c in v.get("claims", []):
            p = prods.get(c.get("product_ref")) or {}
            db = p.get("DB")
            if not isinstance(db, dict):
                skipped["제품 DB 없음"] += 1
                continue
            name = (p.get("match") or {}).get("matched_name") or p.get("product_name") or "이 제품"
            prem = premises_for(c["claim_type"], db, name)
            if not prem:
                skipped[f"{c['claim_type']}: 비교할 공식 자료 없음"] += 1
                plans.append((v, p, c, name, [], None))
                continue
            hyp = make_hypothesis(c.get("text") or "", name)["hypothesis"]
            pairs = [dict(kind=k, premise=pr, hypothesis=hyp) for k, pr in prem]
            plans.append((v, p, c, name, pairs, hyp))
            jobs.extend(pairs)

    print(f"대상 Claim {len(plans)}개 / 문장 쌍 {len(jobs)}개")
    scorer = NLIScorer(model_name=args.model)
    t0 = time.time()
    scores = scorer.score([(j["premise"], j["hypothesis"]) for j in jobs]) if jobs else []
    for j, s in zip(jobs, scores):
        j.update(s)
    print(f"NLI 완료: {time.time() - t0:.1f}초")

    rows = []
    for v, p, c, name, pairs, hyp in plans:
        be = max(pairs, key=lambda x: x["E"]) if pairs else None
        bc = max(pairs, key=lambda x: x["C"]) if pairs else None
        rows.append({
            "video_id": v.get("video_id"), "product_ref": p.get("product_ref"), "제품명": name,
            "claim_id": c.get("claim_id"), "claim_type": c.get("claim_type"), "광고_문장": c.get("text"),
            "가설": hyp, "비교한_문장_수": len(pairs),
            "최대_E": round(be["E"], 4) if be else None, "최대_E_전제": be["premise"] if be else None,
            "최대_C": round(bc["C"], 4) if bc else None, "최대_C_전제": bc["premise"] if bc else None,
            "NLI_결과": judge(be["E"] if be else None, bc["C"] if bc else None) if pairs else "비교 안 함",
        })
    with open(f"{args.prefix}_nli_results.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    by = defaultdict(list)
    for r in rows:
        by[r["claim_type"]].append(r)
    cols = ["E (같은 말)", "C (반대되는 말)", "N (관련 없음)", "애매 (0.1~0.9)", "비교 안 함"]
    md = ["# Claim 유형별 NLI 결과", "", f"- 대상: 제품이 DB와 확정 매핑된 Claim {len(rows)}개", "",
          "| 유형 | Claim 수 | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
    for t, rs in sorted(by.items(), key=lambda x: -len(x[1])):
        cnt = Counter(r["NLI_결과"] for r in rs)
        md.append(f"| {t} | {len(rs)} | " + " | ".join(f"{cnt.get(k, 0)} ({cnt.get(k, 0) / len(rs):.0%})" for k in cols) + " |")
    for t, rs in sorted(by.items(), key=lambda x: -len(x[1])):
        md += ["", f"## {t} 예시", "", "| 광고 문장 | NLI 결과 | 최대 E | 가장 잘 맞은 식약처 문장 |", "|---|---|---|---|"]
        for r in sorted(rs, key=lambda r: -(r["최대_E"] or 0))[:3] + sorted(rs, key=lambda r: (r["최대_E"] or 0))[:2]:
            md.append(f"| {r['광고_문장']} | {r['NLI_결과']} | {r['최대_E']} | {(r['최대_E_전제'] or '').replace('|', '/')} |")
    with open(f"{args.prefix}_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("제외:", dict(skipped))
    print(f"저장: {args.prefix}_nli_results.json, {args.prefix}_report.md")
