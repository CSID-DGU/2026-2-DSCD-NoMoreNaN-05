"""
OVERCLAIM(과장) 판정을 위한 반대 방향 NLI 계산

과장의 정의: 광고가 인정 기능성과 같은 효능을 말하지만, 인정받은 것보다 더 많이 말함
  - 식약처 → 광고 (지금 방식):  식약처 문장만으로 광고를 말할 수 없음   (E 낮음)
  - 광고 → 식약처 (반대 방향):   광고가 맞다면 식약처 문장도 맞음       (E 높음)
  → 두 조건이 함께 성립하면 OVERCLAIM
  예) 식약처 "체지방 감소에 도움" / 광고 "2주 만에 5kg 빠져요"

대상: 이미 계산한 NLI 결과 중 '부합(E ≥ 0.9)이 아닌' 건강 효과 클레임만 (계산량을 줄이기 위해)
      기능성 문장과의 쌍만 뒤집어서 계산함 (주의사항·금지 문장은 그대로)

여러 효능을 한 문장에 담은 클레임 ("혈행·혈중 중성지질 개선")
  → 효능별로 나눠서("혈행 개선", "혈중 중성지질 개선") 각각 정방향·반대 방향을 다시 계산하고 'parts'로 저장
  → summarize.py가 부분별 결과를 합쳐 판정 (전부 부합이면 SUPPORTED, 아니면 가장 심각한 부분의 라벨)
  문장 전체가 이미 부합이면 나누지 않음 (예: "관절 및 연골 건강에 도움" 은 하나의 인정 기능성)

실행:  python run_overclaim.py effect_all_nli_results.json
결과:  effect_all_nli_results_overclaim.json  (클레임마다 reverse_max_E, reverse_best_text 추가)
       overclaim_review.md                     (OVERCLAIM 후보 목록, 사람이 확인용)
다음:  python summarize.py effect_all_nli_results_overclaim.json effect_all_verdicts.json
"""
import argparse
import json
import time

import summarize
from nli import NLIScorer, MODEL_NAME

TAU_HIGH = summarize.TAU_HIGH


from evidence_prep import normalize_text, expand_dots
from hypothesis import make_hypothesis
import re

PRED_TAIL = re.compile(r"(개선|증진|감소|억제|보호|유지|완화|강화|관리|케어|건강|도움[^·&,]*)$")
TRAIL = re.compile(r"\s*(을|를)?\s*(동시에|한번에|한\s*번에|모두|더블\s*케어|트리플\s*케어|집중\s*케어)?\s*[!.~]*\s*$")


def split_claim(text):
    """여러 효능을 한 문장에 담은 광고를 효능별로 나눔. 나눌 수 없으면 []"""
    t = normalize_text(text or "").replace("\n", " ").strip()
    pieces = expand_dots(t)                          # 식약처식 문장 ("A·B에 도움을 줄 수 있음")
    if len(pieces) > 1:
        return pieces
    t = TRAIL.sub("", t)
    t = re.sub(r"(?<=건강)(과|와)\s*", "·", t)        # "장건강과 피부건강" → "장건강·피부건강"
    parts = [x.strip() for x in re.split(r"\s*[·&＆/,，]\s*", t) if x.strip()]
    if len(parts) < 2 or any(len(x) <= 1 for x in parts):
        return []                                    # "영·유아"처럼 한 단어인 경우는 나누지 않음
    m = PRED_TAIL.search(parts[-1])
    tail = m.group(1) if m and m.start() > 0 else None
    out = []
    for x in parts:
        out.append(x if (tail is None or PRED_TAIL.search(x)) else f"{x} {tail}")
    return out


def targets(results):
    """반대 방향을 계산할 클레임: 비교 근거가 있고, 건강 효과 문장이고, 부합이 아닌 것"""
    for v in results:
        for c in v.get("nli_claims", []):
            if c.get("duplicate_of"):
                continue
            f = summarize._recompute_flags(c)
            e = c.get("max_entail_function")
            if c.get("basis") == "NONE" or f.get("is_disclaimer") or not f.get("is_health_claim"):
                continue
            if c.get("is_question") or e is None or e >= TAU_HIGH:
                continue
            yield c


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="verify.py / run_effect.py가 만든 *_nli_results.json")
    ap.add_argument("--model", default=MODEL_NAME)
    args = ap.parse_args()

    with open(args.input, "rb") as f:
        results = json.loads(f.read().decode("utf-8-sig"))

    claims = list(targets(results))
    jobs = []
    for c in claims:
        for x in c.get("checks") or []:
            if x.get("evidence_type") == "FUNCTIONALITY":
                jobs.append((c, x, (x["hypothesis"], x["premise"])))     # 전제 = 광고, 가설 = 식약처 문장

    # 여러 효능을 한 문장에 담은 클레임 → 효능별로 나눠 정방향·반대 방향 계산
    part_jobs = []
    n_split = 0
    for c in claims:
        parts = split_claim(c.get("text"))
        if not parts:
            continue
        n_split += 1
        prem = list(dict.fromkeys(x["premise"] for x in (c.get("checks") or [])
                                  if x.get("evidence_type") == "FUNCTIONALITY"))
        c["parts"] = []
        for part in parts:
            h = make_hypothesis(part, c.get("subject") or "이 제품")["hypothesis"]
            rec = {"text": part, "hypothesis": h}
            c["parts"].append(rec)
            for pr in prem:
                part_jobs.append((rec, "fwd", pr, (pr, h)))
                part_jobs.append((rec, "rev", pr, (h, pr)))
    print(f"대상 클레임 {len(claims)}개 / 반대 방향 문장 쌍 {len(jobs)}개")
    print(f"효능별로 나눈 클레임 {n_split}개 / 부분 문장 쌍 {len(part_jobs)}개")

    scorer = NLIScorer(model_name=args.model)
    t0 = time.time()
    allpairs = [p for _, _, p in jobs] + [p for *_, p in part_jobs]
    allscores = scorer.score(allpairs) if allpairs else []
    scores, pscores = allscores[:len(jobs)], allscores[len(jobs):]
    print(f"NLI 완료: {time.time() - t0:.1f}초")

    for (rec, d, pr, _), sc in zip(part_jobs, pscores):
        k = "max_E" if d == "fwd" else "reverse_E"
        if sc["E"] > rec.get(k, -1):
            rec[k] = round(sc["E"], 4)
            rec["best_text" if d == "fwd" else "reverse_best_text"] = pr

    best = {}
    for (c, x, _), s in zip(jobs, scores):
        k = id(c)
        if k not in best or s["E"] > best[k][0]:
            best[k] = (s["E"], x["ref"], x["premise"], x["hypothesis"])
    for c in claims:
        if id(c) in best:
            e, ref, prem, hyp = best[id(c)]
            c["reverse_max_E"] = round(e, 4)
            c["reverse_best_ref"] = ref
            c["reverse_best_text"] = prem
            c["reverse_best_hypothesis"] = hyp

    out = args.input.replace(".json", "_overclaim.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    cand = sorted([c for c in claims if (c.get("reverse_max_E") or 0) >= TAU_HIGH],
                  key=lambda c: -c["reverse_max_E"])
    lines = ["# OVERCLAIM 후보 (광고 → 식약처 E ≥ 0.9, 식약처 → 광고 E < 0.9)", "",
             f"- 대상 {len(claims)}개 중 후보 {len(cand)}개", "",
             "| 광고 문장 | 식약처 → 광고 E | 광고 → 식약처 E | 식약처 문장 |", "|---|---|---|---|"]
    for c in cand:
        lines.append(f"| {(c.get('text') or '').replace('|', '/')} | {c.get('max_entail_function')} | "
                     f"{c['reverse_max_E']} | {(c.get('reverse_best_text') or '').replace('|', '/')} |")
    lines += ["", "# 효능별로 나눈 클레임", "", "| 광고 문장 | 나눈 부분 | 식약처 → 광고 E | 광고 → 식약처 E | 가장 잘 맞은 식약처 문장 |",
              "|---|---|---|---|---|"]
    for c in claims:
        for p in c.get("parts") or []:
            lines.append(f"| {(c.get('text') or '').replace('|', '/')[:60]} | {p['text']} | {p.get('max_E')} | "
                         f"{p.get('reverse_E')} | {(p.get('best_text') or '').replace('|', '/')} |")
    with open("overclaim_review.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"OVERCLAIM 후보 {len(cand)}개")
    print(f"저장: {out}, overclaim_review.md")
