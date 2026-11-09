"""
Mechanism B 평가: 예측 라벨 vs 정답 라벨(gold_label)

실행:
    python evaluate.py eval_verdicts_mechanism_b.json claims_with_db_labeled.json
결과:
    eval_report.md     정확도, Macro F1, 라벨별 정밀도·재현율·F1, 혼동 행렬 (전체 / EFFECT만 / 여러 유형)
    eval_errors.json   예측과 정답이 다른 클레임 목록 (오류 분석용)

연결 키: video_id + claim_id (정답 파일 안내 기준). 같은 영상에 같은 claim_id가 여러 제품에 있으면 product_ref까지 사용
평가 대상: 정답 파일에서 claim_type에 EFFECT가 들어 있는 클레임
"""
import json
import re
import sys
from collections import Counter, defaultdict

LABELS = ["VIOLATION", "OVERCLAIM", "UNCLEAR", "SUPPORTED", "OUT_OF_SCOPE", "DISCLAIMER"]
SYNTH = re.compile(r"^.{1,60}?\s*제품\s*(은|는|이|가)\s")      # 합성 클레임 형식 ("○○ 제품은 ~") — 추정용


def load(p):
    with open(p, "rb") as f:
        return json.loads(f.read().decode("utf-8-sig"))


def metrics(pairs):
    """pairs: [(gold, pred)] → 정확도, 라벨별 P/R/F1, Macro F1(정답에 나온 라벨 기준), 혼동 행렬"""
    n = len(pairs)
    acc = sum(g == p for g, p in pairs) / n if n else 0
    labels = [l for l in LABELS if any(g == l for g, _ in pairs)]
    per = {}
    for l in labels:
        tp = sum(g == l and p == l for g, p in pairs)
        fp = sum(g != l and p == l for g, p in pairs)
        fn = sum(g == l and p != l for g, p in pairs)
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
        per[l] = {"support": tp + fn, "precision": pr, "recall": rc, "f1": f1}
    macro = sum(v["f1"] for v in per.values()) / len(per) if per else 0
    cm = Counter(pairs)
    return {"n": n, "accuracy": acc, "macro_f1": macro, "per_label": per, "confusion": cm}


def md_block(title, m):
    lines = [f"## {title}", "", f"- 클레임 수: **{m['n']}**",
             f"- 정확도 (Accuracy): **{m['accuracy']:.1%}**", f"- Macro F1: **{m['macro_f1']:.3f}**", "",
             "| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |", "|---|---|---|---|---|"]
    for l, v in m["per_label"].items():
        lines.append(f"| {l} | {v['support']} | {v['precision']:.1%} | {v['recall']:.1%} | {v['f1']:.3f} |")
    pred_labels = [l for l in LABELS if any(p == l for (_, p) in m["confusion"])]
    gold_labels = list(m["per_label"].keys())
    lines += ["", "**혼동 행렬** (행 = 정답, 열 = 예측)", "",
              "| 정답 \\ 예측 | " + " | ".join(pred_labels) + " |", "|---|" + "---|" * len(pred_labels)]
    for g in gold_labels:
        lines.append(f"| {g} | " + " | ".join(str(m["confusion"].get((g, p), 0)) for p in pred_labels) + " |")
    return lines + [""]


if __name__ == "__main__":
    pred_path = sys.argv[1] if len(sys.argv) > 1 else "eval_verdicts_mechanism_b.json"
    gold_path = sys.argv[2] if len(sys.argv) > 2 else "claims_with_db_labeled.json"
    P = load(pred_path)
    preds = P["results"] if isinstance(P, dict) else P
    G = load(gold_path)

    pmap = defaultdict(list)
    for r in preds:
        pmap[(r["video_id"], r["claim_id"])].append(r)

    rows, missing = [], []
    for v in G:
        for c in v.get("claims", []):
            ct = c.get("claim_type")
            ct = ct if isinstance(ct, list) else [ct]
            if "EFFECT" not in ct:
                continue
            cand = pmap.get((v["video_id"], c["claim_id"]), [])
            cand = [r for r in cand if r.get("product_ref") == c.get("product_ref")] or cand
            if not cand:
                missing.append((v["video_id"], c["claim_id"]))
                continue
            r = cand[0]
            rows.append({"video_id": v["video_id"], "claim_id": c["claim_id"], "product_ref": c.get("product_ref"),
                         "claim_type": ct, "text": c.get("text"), "gold": c["gold_label"], "pred": r["label"],
                         "reason_code": r.get("reason_code"), "evidence_text": r.get("evidence_text"),
                         "scores": r.get("scores"), "synthetic_guess": bool(SYNTH.match(c.get("text") or ""))})

    allm = metrics([(x["gold"], x["pred"]) for x in rows])
    only = metrics([(x["gold"], x["pred"]) for x in rows if x["claim_type"] == ["EFFECT"]])
    multi = metrics([(x["gold"], x["pred"]) for x in rows if x["claim_type"] != ["EFFECT"]])
    real = metrics([(x["gold"], x["pred"]) for x in rows if not x["synthetic_guess"]])

    lines = ["# Mechanism B 평가 결과", "",
             f"- 예측 파일: `{pred_path}` / 정답 파일: `{gold_path}`",
             f"- 평가 대상: 정답 파일에서 claim_type에 EFFECT가 들어 있는 클레임 {len(rows) + len(missing)}개",
             f"- 예측이 없는 클레임: {len(missing)}개", ""]
    lines += md_block("1. 전체 (EFFECT 포함 클레임)", allm)
    lines += md_block("2. EFFECT만 있는 클레임", only)
    lines += md_block("3. 여러 유형이 함께 있는 클레임 (예: EFFECT + QUANTITY)", multi)
    lines += md_block("4. 합성 클레임 제외 (\"○○ 제품은 ~\" 형식을 합성으로 추정해 제외)", real)
    errs = Counter((x["gold"], x["pred"]) for x in rows if x["gold"] != x["pred"])
    lines += ["## 5. 자주 틀린 경우", "", "| 정답 | 예측 | 개수 |", "|---|---|---|"]
    lines += [f"| {g} | {p} | {n} |" for (g, p), n in errs.most_common(10)]
    with open("eval_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open("eval_errors.json", "w", encoding="utf-8") as f:
        json.dump([x for x in rows if x["gold"] != x["pred"]], f, ensure_ascii=False, indent=2)
    print(f"평가 {len(rows)}개 / 예측 없음 {len(missing)}개")
    print(f"정확도 {allm['accuracy']:.1%} / Macro F1 {allm['macro_f1']:.3f}")
    print("저장: eval_report.md, eval_errors.json")
