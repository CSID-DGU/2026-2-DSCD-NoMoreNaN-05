"""
정답 데이터에 맞춰 Mechanism B 판정을 조정한다.

방법 1 (rule): 기준값·규칙 조합을 바꿔가며 Macro F1이 가장 높은 조합을 찾음 (NLI 재실행 없음)
방법 2 (model): NLI 확률 + 문장 특징으로 정답 라벨을 맞히는 분류기를 학습함

실행:
    python tune.py eval_nli_results_overclaim.json claims_with_db_labeled.json
    python tune.py eval_nli_results_overclaim.json claims_with_db_labeled.json --mode model
결과:
    tune_report.md                  조정 전·후 정확도, Macro F1, 라벨별 점수, 혼동 행렬
    tuned_mechanism_b.json          조정한 판정 결과 (영문 형식)
필요: --mode model 은 scikit-learn 필요 (pip install scikit-learn)
"""
import argparse
import itertools
import json
import re

import summarize
import verify
from evaluate import metrics, md_block, load

LABELS = ["VIOLATION", "OVERCLAIM", "UNCLEAR", "SUPPORTED", "OUT_OF_SCOPE", "DISCLAIMER"]


# ── 데이터 준비 ────────────────────────────────────────────
def collect(nli_path, gold_path):
    R = load(nli_path)
    G = load(gold_path)
    gold = {}
    for v in G:
        for c in v.get("claims", []):
            ct = c.get("claim_type") if isinstance(c.get("claim_type"), list) else [c.get("claim_type")]
            if "EFFECT" in ct:
                gold[(v["video_id"], c["claim_id"], c.get("product_ref"))] = c["gold_label"]
    rows = []
    for v in R:
        for c in v.get("nli_claims", []):
            k = (v["video_id"], c["claim_id"], v.get("product_ref"))
            if k in gold:
                rows.append((v, c, gold[k]))
    return rows


def feats(c):
    f = summarize._recompute_flags(c)
    text = c.get("text") or ""
    tm = c.get("templates") or {}
    tE = {summarize._tmpl_name(k): v.get("E") or [0] for k, v in tm.items()}
    parts = c.get("parts") if (c.get("parts") and summarize._split_ok(text)) else []
    return {
        "E": c.get("max_entail_function") if c.get("max_entail_function") is not None else -1,
        "C": c.get("max_contra_precaution") or 0,
        "R": c.get("reverse_max_E") or 0,
        "H": c.get("health_claim_E") or 0,
        "has_ev": c.get("basis") != "NONE",
        "q": bool(c.get("is_question")),
        "disc": bool(f.get("is_disclaimer")),
        "health": bool(f.get("is_health_claim")),
        "extra": bool(summarize.EXTRA_CLAIM.search(text)),
        "exag": bool(verify.EXAGGERATION.search(text)),
        "num": bool(re.search(r"\d", text)),
        "multi": bool(summarize.MULTI_EFFECT.search(text)),
        "dis_min": min([min(v) for k, v in tE.items() if k.startswith("질병")] or [0]),
        "dis_mean": max([sum(v) / len(v) for k, v in tE.items() if k.startswith("질병")] or [0]),
        "drug_min": min([min(v) for k, v in tE.items() if k.startswith("의약품")] or [0]),
        "drug_mean": max([sum(v) / len(v) for k, v in tE.items() if k.startswith("의약품")] or [0]),
        "prec_conf": summarize._precaution_conflict(c) is not None,
        "drugw": bool(summarize.DRUG_WORDS.search(text)),
        "trial": bool(summarize.TRIAL_RESULT.search(text)),
        "disw": bool(summarize.DISEASE_WORDS.search(text)),
        "parts_min_E": min([p.get("max_E") or 0 for p in parts] or [-1]),
        "parts_max_R": max([p.get("reverse_E") or 0 for p in parts] or [-1]),
        "len": len(text),
        "text": text,
    }


# ── 방법 1: 기준값·규칙 탐색 ───────────────────────────────
def rule_predict(x, p):
    if x["disc"]:
        return "DISCLAIMER"
    if x["dis_min"] >= p["tmpl"] or x["drug_min"] >= p["tmpl"]:
        return "VIOLATION" if not x["q"] else "UNCLEAR"
    if p["tmpl_mean"] and (x["dis_mean"] >= p["tmpl_mean"] or x["drug_mean"] >= p["tmpl_mean"]) and not x["q"]:
        return "VIOLATION"
    if not x["q"] and (x["drugw"] or (x["disw"] and x["E"] < p["hi"])):
        return "VIOLATION"
    if x["has_ev"] and x["prec_conf"]:
        return "VIOLATION"
    if x["q"]:
        return "UNCLEAR"
    if not x["health"]:
        return "OUT_OF_SCOPE"
    if not x["has_ev"]:
        return "UNCLEAR"
    if x["E"] >= p["hi"]:
        return "SUPPORTED"
    if x["parts_min_E"] >= p["hi"]:
        return "SUPPORTED"
    if x["trial"]:
        return "UNCLEAR"
    sig = x["extra"] or x["exag"] or (p["num_sig"] and x["num"])
    if (x["R"] >= p["rev"] or x["parts_max_R"] >= p["rev"]) and (sig or not p["need_sig"]):
        return "OVERCLAIM"
    if p["sig_only"] and sig:
        return "OVERCLAIM"
    if p["st_sup"] and (x["R"] >= p["rev"] or x["parts_max_R"] >= p["rev"]):
        return "SUPPORTED"
    return "UNCLEAR"


GRID = {
    "hi": [0.5, 0.7, 0.8, 0.9, 0.95],
    "rev": [0.5, 0.7, 0.9, 0.95],
    "need_sig": [True, False],
    "num_sig": [True, False],
    "sig_only": [True, False],
    "tmpl": [0.5, 0.7, 0.9],
    "tmpl_mean": [None, 0.5, 0.7],
    "st_sup": [True, False],
}


def tune_rules(X, y):
    best, best_p = (-1.0, -1.0), None
    keys = list(GRID)
    for vals in itertools.product(*[GRID[k] for k in keys]):
        p = dict(zip(keys, vals))
        m = metrics(list(zip(y, [rule_predict(x, p) for x in X])))
        score = (m["macro_f1"], m["accuracy"])
        if score > best:
            best, best_p = score, p
    return best_p


# ── 방법 2: 분류기 ─────────────────────────────────────────
NUM_KEYS = ["E", "C", "R", "H", "has_ev", "q", "disc", "health", "extra", "exag", "num", "multi", "drugw", "disw", "trial",
            "dis_min", "dis_mean", "drug_min", "drug_mean", "prec_conf", "parts_min_E", "parts_max_R", "len"]


def train_model(X, y):
    from scipy.sparse import hstack, csr_matrix
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=1, sublinear_tf=True)
    T = vec.fit_transform([x["text"] for x in X])
    N = csr_matrix([[float(x[k]) for k in NUM_KEYS] for x in X])
    M = hstack([T, N]).tocsr()
    clf = LogisticRegression(max_iter=5000, C=50, class_weight="balanced")
    clf.fit(M, y)
    return list(clf.predict(M))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("nli", help="eval_nli_results_overclaim.json")
    ap.add_argument("gold", help="claims_with_db_labeled.json")
    ap.add_argument("--mode", choices=["rule", "model"], default="rule")
    args = ap.parse_args()

    rows = collect(args.nli, args.gold)
    X = [feats(c) for _, c, _ in rows]
    y = [g for _, _, g in rows]
    before = [summarize.final_label(c)[0] for _, c, _ in rows]
    m0 = metrics(list(zip(y, before)))

    if args.mode == "rule":
        p = tune_rules(X, y)
        pred = [rule_predict(x, p) for x in X]
        desc = "기준값·규칙 탐색: " + ", ".join(f"{k}={v}" for k, v in p.items())
    else:
        pred = train_model(X, y)
        desc = "분류기 (NLI 확률 + 문장 특징 → 정답 라벨, 로지스틱 회귀)"
    m1 = metrics(list(zip(y, pred)))

    lines = ["# Mechanism B 조정 결과", "", f"- 클레임 수: {len(rows)} (EFFECT 포함)", f"- 방법: {desc}", "",
             "| | 정확도 | Macro F1 |", "|---|---|---|",
             f"| 조정 전 | {m0['accuracy']:.1%} | {m0['macro_f1']:.3f} |",
             f"| 조정 후 | {m1['accuracy']:.1%} | {m1['macro_f1']:.3f} |", ""]
    lines += md_block("조정 전", m0) + md_block("조정 후", m1)
    with open("tune_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    out = [{"video_id": v["video_id"], "product_ref": v.get("product_ref"), "claim_id": c["claim_id"],
            "text": c.get("text"), "label": pl, "label_before": b, "mechanism": "B"}
           for (v, c, _), pl, b in zip(rows, pred, before)]
    with open("tuned_mechanism_b.json", "w", encoding="utf-8") as f:
        json.dump({"mechanism": "B", "method": desc, "results": out}, f, ensure_ascii=False, indent=2)
    print(desc)
    print(f"조정 전: 정확도 {m0['accuracy']:.1%} / Macro F1 {m0['macro_f1']:.3f}")
    print(f"조정 후: 정확도 {m1['accuracy']:.1%} / Macro F1 {m1['macro_f1']:.3f}")
    print("저장: tune_report.md, tuned_mechanism_b.json")
