"""
TRUEAD NLI 모듈
(전제, 가설) 쌍 목록을 받아 쌍마다 Entailment / Neutral / Contradiction 확률을 돌려준다.

- 무엇을 전제로, 무엇을 가설로 넣을지는 호출하는 쪽이 정한다.
  (1·2호 템플릿: 전제 = 광고 주장 / 4호 나: 전제 = 공식 기능성 문장)
- 라벨(VIOLATION 등)은 여기서 정하지 않는다. 확률만 돌려준다.
- 실행:  python nli.py   (자체 테스트가 돌아간다)
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "Huffon/klue-roberta-base-nli"   # 비교 후보: large 체크포인트

# 체크포인트의 라벨 이름이 LABEL_0 같은 일반 이름일 때만 쓰는 예비 순서.
# KLUE-NLI 데이터셋의 라벨 순서(0=entailment, 1=neutral, 2=contradiction)를 가정한 값이므로,
# 이 값을 쓴 경우에는 반드시 아래 자체 테스트 결과로 순서가 맞는지 확인해야 한다.
KLUE_FALLBACK_ORDER = {"E": 0, "N": 1, "C": 2}


class NLIScorer:
    def __init__(self, model_name=MODEL_NAME, device=None, batch_size=32):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device).eval()
        self.batch_size = batch_size
        self.id2label = self.model.config.id2label
        self.label_idx, self.used_fallback = self._resolve_labels(self.id2label)

    @staticmethod
    def _resolve_labels(id2label):
        """라벨 이름을 보고 E/N/C가 몇 번째 칸인지 찾는다. 체크포인트마다 순서가 다르기 때문."""
        found = {}
        for idx, name in id2label.items():
            n = str(name).lower()
            if n.startswith("entail"):
                found["E"] = int(idx)
            elif n.startswith("neutral"):
                found["N"] = int(idx)
            elif n.startswith("contra"):
                found["C"] = int(idx)
        if len(found) == 3:
            return found, False
        print(f"[경고] 라벨 이름을 해석하지 못해 KLUE 기본 순서를 가정합니다: {id2label}")
        print("       아래 자체 테스트에서 기대 결과와 맞는지 꼭 확인하세요.")
        return dict(KLUE_FALLBACK_ORDER), True

    @torch.no_grad()
    def score(self, pairs):
        """
        pairs: [(전제, 가설), ...]
        반환:  [{"E": 0.xx, "N": 0.xx, "C": 0.xx}, ...]  (입력 순서 그대로)
        같은 쌍이 여러 번 나오면 한 번만 계산한다.
        """
        unique = list(dict.fromkeys(pairs))
        cache = {}
        for start in range(0, len(unique), self.batch_size):
            batch = unique[start:start + self.batch_size]
            enc = self.tokenizer(
                [p for p, _ in batch],
                [h for _, h in batch],
                padding=True,
                truncation=True,
                max_length=512,
                return_token_type_ids=False,   # KLUE-RoBERTa는 문장 구분 번호(token_type)를 1종류만 받음
                return_tensors="pt",
            ).to(self.device)
            probs = torch.softmax(self.model(**enc).logits, dim=-1).cpu()
            for pair, row in zip(batch, probs):
                cache[pair] = {k: round(float(row[i]), 4) for k, i in self.label_idx.items()}
        return [cache[p] for p in pairs]


if __name__ == "__main__":
    scorer = NLIScorer()
    print("모델:", MODEL_NAME, "| 장치:", scorer.device)
    print("id2label:", scorer.id2label)
    print("해석된 라벨 위치:", scorer.label_idx, "| 예비 순서 사용:", scorer.used_fallback)
    print("-" * 70)

    # (전제, 가설, 기대 결과)
    tests = [
        ("체지방 감소에 도움을 줄 수 있다", "살 빠지는 데 도움을 준다", "E"),
        ("탄수화물이 지방으로 합성되는 것을 억제하여 체지방 감소에 도움을 줄 수 있다",
         "지방을 직접 분해한다", "N"),
        ("혈행 개선에 도움을 줄 수 있다", "혈관 내벽을 보호한다", "N"),
        ("임산부와 수유부는 섭취에 주의해야 한다", "임산부도 안심하고 먹어도 된다", "C"),
    ]
    results = scorer.score([(p, h) for p, h, _ in tests])
    ok = 0
    for (p, h, expect), r in zip(tests, results):
        top = max(r, key=r.get)
        ok += top == expect
        mark = "OK " if top == expect else "확인"
        print(f"[{mark}] 기대 {expect} / 결과 {top}  E={r['E']:.2f} N={r['N']:.2f} C={r['C']:.2f}")
        print(f"       전제: {p}")
        print(f"       가설: {h}")
    print("-" * 70)
    print(f"기대와 일치: {ok}/{len(tests)}")
