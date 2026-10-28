"""
nli_input_example.json의 (전제, 가설) 쌍을 NLI로 돌려 본다.
같은 쌍을 '주어를 붙인 버전'과 '주어를 뺀 버전'으로 각각 돌려서 비교한다.

실행:  python run_example.py
필요한 파일(같은 폴더): nli.py, nli_input_example.json
"""
import json
from nli import NLIScorer


def strip_subject(text, target):
    """'고려홍삼정은 면역력 …' → '면역력 …'  (주어를 뺀 비교용 문장)"""
    for p in ("은 ", "는 ", "이 ", "가 "):
        if text.startswith(target + p):
            return text[len(target + p):]
    return text


data = json.load(open("nli_input_example.json", encoding="utf-8"))
scorer = NLIScorer()

for claim in data["claims"]:
    target = claim["target"]
    print("=" * 78)
    print(f"[{claim['claim_id']}] 가설: {claim['hypothesis']}")
    print(f"기대: {claim['expected']}")
    with_subj = [(x["premise"], x["hypothesis"]) for x in claim["pairs"]]
    no_subj = [(strip_subject(p, target), strip_subject(h, target)) for p, h in with_subj]
    r1 = scorer.score(with_subj)
    r2 = scorer.score(no_subj)
    for pair, a, b in zip(claim["pairs"], r1, r2):
        top_a, top_b = max(a, key=a.get), max(b, key=b.get)
        print(f"  {pair['premise_ref']:<14} 주어O: {top_a} (E={a['E']:.2f} N={a['N']:.2f} C={a['C']:.2f})"
              f" | 주어X: {top_b} (E={b['E']:.2f} N={b['N']:.2f} C={b['C']:.2f})")
        print(f"      전제: {pair['premise']}")
