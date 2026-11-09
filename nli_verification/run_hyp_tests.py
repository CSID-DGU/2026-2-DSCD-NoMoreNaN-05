"""
가설 만들기 효과 실험
같은 광고 주장을 세 가지 버전으로 NLI에 넣고 결과를 비교한다.

  V1 원문 조각     : 추출된 문장 그대로            ("혈류 흐름을 원활하게 해주고")
  V2 주어만 맞춤   : 주어만 붙이고 끝은 그대로     ("베르베린은 혈류 흐름을 원활하게 해주고")
  V3 주어+끝 정리  : make_hypothesis() 전체 적용  ("베르베린은 혈류 흐름을 원활하게 해 준다")

전제는 세 버전 모두 같다: make_premise(target, premise_core)

실행:  python run_hyp_tests.py
필요한 파일(같은 폴더): nli.py, evidence_prep.py, hypothesis.py, hyp_tests.csv
결과:  화면 출력 + hyp_test_results.csv
"""
import csv
from nli import NLIScorer
from evidence_prep import make_premise
from hypothesis import make_hypothesis

tests = list(csv.DictReader(open("hyp_tests.csv", encoding="utf-8-sig")))
VERSIONS = ["V1 원문 조각", "V2 주어만", "V3 주어+끝"]

rows, pairs = [], []
for t in tests:
    premise = make_premise(t["target"], t["premise_core"])
    hyps = [t["span"],
            make_hypothesis(t["span"], t["target"], fix_ending=False)["hypothesis"],
            make_hypothesis(t["span"], t["target"])["hypothesis"]]
    for v, h in zip(VERSIONS, hyps):
        pairs.append((premise, h))
        rows.append({"id": t["id"], "version": v, "premise": premise, "hypothesis": h,
                     "expected": t["expected"], "note": t["note"]})

scorer = NLIScorer()
for row, r in zip(rows, scorer.score(pairs)):
    row.update(pred=max(r, key=r.get), E=f"{r['E']:.2f}", N=f"{r['N']:.2f}", C=f"{r['C']:.2f}")

# 버전별 일치율
print("\n[버전별 일치율] (기대 '?'는 제외)")
for v in VERSIONS:
    graded = [x for x in rows if x["version"] == v and x["expected"] in ("E", "N", "C")]
    ok = sum(x["pred"] == x["expected"] for x in graded)
    e_graded = [x for x in graded if x["expected"] == "E"]
    e_ok = sum(x["pred"] == "E" for x in e_graded)
    print(f"  {v:<12} 전체 {ok}/{len(graded)}   (같은 뜻 주장을 E로 맞힌 것 {e_ok}/{len(e_graded)})")

# 사례별 비교
print("\n[사례별 결과]")
for t in tests:
    print(f"\n{t['id']} 기대 {t['expected']}  ({t['note']})")
    for x in [x for x in rows if x["id"] == t["id"]]:
        mark = "" if t["expected"] not in ("E", "N", "C") else (" ✔" if x["pred"] == t["expected"] else " ✘")
        print(f"  {x['version']:<12} {x['pred']}{mark} (E={x['E']} N={x['N']} C={x['C']})  {x['hypothesis']}")
    print(f"  {'전제':<12} {rows[[r['id'] for r in rows].index(t['id'])]['premise']}")

with open("hyp_test_results.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("\n저장: hyp_test_results.csv")
