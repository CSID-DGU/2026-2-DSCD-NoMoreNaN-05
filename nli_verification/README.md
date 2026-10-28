# NLI Verification (Mechanism B)

광고 주장이 식약처 공식 문장과 **같은 말인지(E), 관련 없는지(N), 반대되는 말인지(C)**를
KLUE-RoBERTa NLI 모델로 판단하는 모듈.
NLI는 확률만 내고, 최종 라벨(인정됨 / 인정 안 됨 / 충돌 / 판단 보류)은 판정 단계에서 정함.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `nli.py` | NLI 모델 실행. (전제, 가설) 쌍 → E·N·C 확률 |
| `evidence_prep.py` | 식약처 기능성·주의사항 원문을 "기능성 1개 = 문장 1개"로 정리 |
| `hypothesis.py` | 광고 원문 조각 → 가설 문장 (주어 통일, 문장 끝 정리, 질문 표시, 동의어 바꾸기) |
| `verify.py` | 전체 연결. 광고 주장 + 제품 ID → 판정용 결과 JSON. 질병·의약품 표현 검사 포함 |
| `build_premises_db.py` | 정리된 문장을 SQLite DB(`nli_premises.sqlite`)로 만듦 |
| `run_example.py` | 실제 DB 문장 예시 실행 |
| `run_tests.py`, `nli_tests.csv` | 1차 실험 (상황별 30쌍) |
| `run_hyp_tests.py`, `hyp_tests.csv` | 2차 실험 (가설 만들기 효과) |
| `nli_input_example.json` | NLI 입력 예시 |

## 설치

```bash
python -m venv nli_env
source nli_env/bin/activate
pip install -r requirements.txt
```
서버 디스크가 느리면 CPU용 torch가 가벼움:
`pip install torch --index-url https://download.pytorch.org/whl/cpu`

## 실행 순서

**1. DB에서 원본 데이터 뽑기** (저장소에는 포함하지 않음)

```bash
python -c "
import sqlite3, csv
src = 'claim_verification.sqlite 경로'
con = sqlite3.connect(f'file:{src}?mode=ro&immutable=1', uri=True)
for name, q in [('products_selected.csv', 'SELECT product_id, product_name, company_name, main_functionality, intake_method, intake_precautions FROM products'),
                ('evidence.csv', 'SELECT * FROM evidence')]:
    cur = con.execute(q)
    with open(name, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow([d[0] for d in cur.description]); w.writerows(cur)
"
```

**2. 식약처 문장 정리 → DB 만들기**

```bash
python evidence_prep.py products_selected.csv evidence.csv
python build_premises_db.py
```

**3. 검증 실행**

```bash
python verify.py              # 2번 제품으로 데모
python verify.py --save       # 결과를 nli_result 테이블에 저장
python verify.py --model 모델이름   # 다른 NLI 모델로 실행 (large 비교용)
```

## 입력과 출력

입력 (광고 주장)
```json
{"claim_id": "c1", "text": "이 제품은 면역력을 높여 줍니다", "target": "고려홍삼정", "target_kind": "product"}
```

출력 (판정 단계로 넘김, 일부)
```json
{
  "claim_id": "c1",
  "hypothesis": "고려홍삼정은 면역력을 높여 준다",
  "is_question": false,
  "basis": "PRODUCT",
  "max_entail_function": 0.99,
  "best_function_text": "고려홍삼정은 면역력 증진에 도움을 줄 수 있다",
  "max_contra_precaution": 0.01
}
```

## 주의

- 기준값(0.9 / 0.1)은 임시값이며 정답 데이터로 조정 예정
- `nli_premises.sqlite`(약 120MB) 등 큰 데이터는 GitHub에 올리지 않고 위 순서로 다시 만듦
