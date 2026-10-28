"""
NLI 실험: nli_tests.csv의 (전제, 가설) 쌍을 돌려서 기대 결과와 비교한다.

실행:
    python run_tests.py                       # 기본 모델(base)만
    python run_tests.py 모델이름1 모델이름2      # 여러 모델 비교 (예: base와 large)

필요한 파일(같은 폴더): nli.py, nli_tests.csv
결과:
    화면에 그룹별 일치율과 기대와 다른 사례를 출력
    nli_test_results.csv 에 모든 쌍의 확률 저장 (노션 정리용)

expected 열
    E / N / C : 기대 결과. 일치율 계산에 들어감
    ?         : 정답을 정하지 않고 모델 반응만 관찰. 일치율 계산에서 빠짐
"""
import csv
import sys
from collections import defaultdict
from nli import NLIScorer, MODEL_NAME

models = sys.argv[1:] or [MODEL_NAME]
tests = list(csv.DictReader(open("nli_tests.csv", encoding="utf-8-sig")))
pairs = [(t["premise"], t["hypothesis"]) for t in tests]

all_rows = []
for model in models:
    print("=" * 78)
    print("모델:", model)
    scorer = NLIScorer(model_name=model)
    results = scorer.score(pairs)

    by_group = defaultdict(lambda: [0, 0])          # 그룹 → [일치, 채점 대상]
    misses, observed = [], []
    saturated = 0
    for t, r in zip(tests, results):
        pred = max(r, key=r.get)
        saturated += max(r.values()) >= 0.99
        exp = t["expected"].strip()
        if exp in ("E", "N", "C"):
            by_group[t["group"]][1] += 1
            if pred == exp:
                by_group[t["group"]][0] += 1
            else:
                misses.append((t, pred, r))
        else:
            observed.append((t, pred, r))
        all_rows.append({"model": model, **t, "pred": pred,
                         "E": f"{r['E']:.3f}", "N": f"{r['N']:.3f}", "C": f"{r['C']:.3f}",
                         "match": "" if exp not in ("E", "N", "C") else int(pred == exp)})

    print("\n[그룹별 일치율]")
    total_ok = total_n = 0
    for g, (ok, n) in by_group.items():
        print(f"  {g:<10} {ok}/{n}")
        total_ok += ok
        total_n += n
    print(f"  {'전체':<10} {total_ok}/{total_n}")
    print(f"\n[확률 쏠림] 가장 높은 확률이 0.99 이상인 쌍: {saturated}/{len(tests)}")

    print("\n[기대와 다른 사례]")
    for t, pred, r in misses:
        print(f"  {t['id']} 기대 {t['expected']} → 결과 {pred}  (E={r['E']:.2f} N={r['N']:.2f} C={r['C']:.2f})  {t['note']}")
        print(f"      전제: {t['premise']}")
        print(f"      가설: {t['hypothesis']}")

    print("\n[관찰용 사례 (기대 '?')]")
    for t, pred, r in observed:
        print(f"  {t['id']} 결과 {pred}  (E={r['E']:.2f} N={r['N']:.2f} C={r['C']:.2f})  {t['note']}")

with open("nli_test_results.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
    w.writeheader()
    w.writerows(all_rows)
print("\n저장: nli_test_results.csv")
