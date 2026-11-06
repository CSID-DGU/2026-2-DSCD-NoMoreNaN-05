"""최종 결과 파일 + 정답 파일 → 성능평가 보고서.

    python -m claim_verification.evaluation.run final_results.json gold.json out_dir

out_dir에 쓰는 파일
    eval_report.json   지표 전체(아래 구분별)
    eval_report.md     사람이 읽는 표
    eval_errors.json   최종 라벨이 정답과 다른 클레임

구분
    overall            전체 클레임의 최종 라벨
    by_source          최종 라벨을 만든 결과가 A만 / B만 / A·B 둘 다 있는 클레임 / 둘 다 없는 클레임(제품 미확정 skipped)
    by_claim_type      claim_type 조합별("COMPOSITION+QUANTITY")
    a_only_label       A 결과가 있는 클레임에서 A 라벨만 정답과 비교
    b_only_label       B 결과가 있는 클레임에서 B 라벨만 정답과 비교(B 담당 평가와 같은 기준)
    merge_changes      A·B가 모두 있는데 최종 라벨이 B 라벨과 달라진 클레임: 바뀌기 전후 정답 여부
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from ..final.merge import LABELS
from .join import join
from .metrics import evaluate

A_ONLY, B_ONLY, BOTH, NONE = "A만", "B만", "A·B", "결과 없음"


def _source(row: dict) -> str:
    if row["A"] and row["B"]:
        return BOTH
    if row["A"] or row["B"]:
        return A_ONLY if row["A"] else B_ONLY
    return NONE


def _type_key(row: dict) -> str:
    return "+".join(row["claim_type"] or []) or "(없음)"


def _metrics(rows: list[dict], pred=lambda r: r["pred"]) -> dict:
    return evaluate([(r["gold"], pred(r)) for r in rows], LABELS)


def _grouped(rows: list[dict], key) -> dict:
    groups = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    return {k: _metrics(v) for k, v in sorted(groups.items(), key=lambda kv: -len(kv[1]))}


def _merge_changes(rows: list[dict]) -> dict:
    changed = [r for r in rows if r["A"] and r["B"] and r["pred"] != r["B"]["label"]]
    outcome = Counter()
    for r in changed:
        before, after = r["B"]["label"] == r["gold"], r["pred"] == r["gold"]
        outcome["맞음→맞음" if before and after else "틀림→맞음" if after else "맞음→틀림" if before else "틀림→틀림"] += 1
    return {"n": len(changed), "outcome": dict(outcome),
            "transitions": dict(Counter(f"{r['B']['label']}→{r['pred']}" for r in changed))}


def report(rows: list[dict]) -> dict:
    with_a = [r for r in rows if r["A"]]
    with_b = [r for r in rows if r["B"]]
    return {
        "overall": _metrics(rows),
        "by_source": _grouped(rows, _source),
        "by_claim_type": _grouped(rows, _type_key),
        "a_only_label": _metrics(with_a, lambda r: r["A"]["label"]),
        "b_only_label": _metrics(with_b, lambda r: r["B"]["label"]),
        "merge_changes": _merge_changes(rows),
    }


def _pct(x: float) -> str:
    return f"{x:.1%}"


def _summary_line(name: str, m: dict) -> str:
    return f"| {name} | {m['n']} | {_pct(m['accuracy'])} | {m['macro_f1']:.3f} |"


def to_markdown(rep: dict, meta: dict) -> str:
    o = rep["overall"]
    lines = ["# 성능평가", "", f"- 최종 결과: `{meta['final']}`", f"- 정답: `{meta['gold']}`",
             f"- B 출처: `{meta.get('b_source')}`", "",
             "## 전체", "", f"- 클레임 {o['n']}건, 정확도 **{_pct(o['accuracy'])}**, Macro F1 **{o['macro_f1']:.3f}**", "",
             "| 라벨 | 정답 수 | 예측 수 | 정밀도 | 재현율 | F1 |", "|---|---|---|---|---|---|"]
    for label in LABELS:
        s = o["labels"][label]
        lines.append(f"| {label} | {s['support']} | {s['predicted']} | {_pct(s['precision'])} | {_pct(s['recall'])} | {s['f1']:.3f} |")
    lines += ["", "**혼동행렬** (행 = 정답, 열 = 예측)", "", "| 정답 \\ 예측 | " + " | ".join(LABELS) + " |",
              "|---|" + "---|" * len(LABELS)]
    lines += [f"| {g} | " + " | ".join(str(o["confusion"][g][p]) for p in LABELS) + " |" for g in LABELS]
    table = ["| 구분 | 건수 | 정확도 | Macro F1 |", "|---|---|---|---|"]
    lines += ["", "## 결과를 낸 쪽별", "", *table, *[_summary_line(k, m) for k, m in rep["by_source"].items()]]
    lines += ["", "## A·B 라벨 단독", "", *table, _summary_line("A 라벨 (A 결과 있는 클레임)", rep["a_only_label"]),
              _summary_line("B 라벨 (B 결과 있는 클레임)", rep["b_only_label"])]
    mc = rep["merge_changes"]
    lines += ["", "## 합치면서 B 라벨이 바뀐 클레임", "", f"- {mc['n']}건: {mc['outcome']}", f"- 바뀐 방향: {mc['transitions']}"]
    lines += ["", "## claim_type 조합별", "", *table, *[_summary_line(k, m) for k, m in rep["by_claim_type"].items()], ""]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    final_path, gold_path, out_dir = argv
    final = json.loads(Path(final_path).read_text(encoding="utf-8"))
    gold = json.loads(Path(gold_path).read_text(encoding="utf-8"))
    rows = join(final["results"], gold)
    rep = report(rows)
    meta = {"final": final_path, "gold": gold_path, "b_source": final.get("meta", {}).get("b_source")}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "eval_report.json").write_text(json.dumps({"meta": meta, **rep}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "eval_report.md").write_text(to_markdown(rep, meta), encoding="utf-8")
    errors = [r for r in rows if r["gold"] != r["pred"]]
    (out / "eval_errors.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
    o = rep["overall"]
    print(f"전체 {o['n']}건 정확도 {_pct(o['accuracy'])} Macro F1 {o['macro_f1']:.3f}, 오답 {len(errors)}건", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
