# Mechanism B 평가 결과

- 예측 파일: `eval_verdicts_mechanism_b.json` / 정답 파일: `claims_with_db_labeled.json`
- 평가 대상: 정답 파일에서 claim_type에 EFFECT가 들어 있는 클레임 681개
- 예측이 없는 클레임: 0개

## 1. 전체 (EFFECT 포함 클레임)

- 클레임 수: **681**
- 정확도 (Accuracy): **69.8%**
- Macro F1: **0.768**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 47 | 100.0% | 95.7% | 0.978 |
| OVERCLAIM | 66 | 92.9% | 98.5% | 0.956 |
| UNCLEAR | 174 | 51.6% | 54.6% | 0.531 |
| SUPPORTED | 281 | 72.2% | 76.9% | 0.745 |
| OUT_OF_SCOPE | 88 | 50.0% | 33.0% | 0.397 |
| DISCLAIMER | 25 | 100.0% | 100.0% | 1.000 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 45 | 0 | 1 | 1 | 0 | 0 |
| OVERCLAIM | 0 | 65 | 0 | 0 | 1 | 0 |
| UNCLEAR | 0 | 3 | 95 | 59 | 17 | 0 |
| SUPPORTED | 0 | 1 | 53 | 216 | 11 | 0 |
| OUT_OF_SCOPE | 0 | 1 | 35 | 23 | 29 | 0 |
| DISCLAIMER | 0 | 0 | 0 | 0 | 0 | 25 |

## 2. EFFECT만 있는 클레임

- 클레임 수: **523**
- 정확도 (Accuracy): **74.6%**
- Macro F1: **0.781**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 45 | 100.0% | 100.0% | 1.000 |
| OVERCLAIM | 66 | 98.5% | 98.5% | 0.985 |
| UNCLEAR | 97 | 45.7% | 54.6% | 0.498 |
| SUPPORTED | 218 | 77.8% | 82.1% | 0.799 |
| OUT_OF_SCOPE | 72 | 56.1% | 31.9% | 0.407 |
| DISCLAIMER | 25 | 100.0% | 100.0% | 1.000 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 45 | 0 | 0 | 0 | 0 | 0 |
| OVERCLAIM | 0 | 65 | 0 | 0 | 1 | 0 |
| UNCLEAR | 0 | 0 | 53 | 31 | 13 | 0 |
| SUPPORTED | 0 | 1 | 34 | 179 | 4 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 29 | 20 | 23 | 0 |
| DISCLAIMER | 0 | 0 | 0 | 0 | 0 | 25 |

## 3. 여러 유형이 함께 있는 클레임 (예: EFFECT + QUANTITY)

- 클레임 수: **158**
- 정확도 (Accuracy): **53.8%**
- Macro F1: **0.376**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 2 | 0.0% | 0.0% | 0.000 |
| UNCLEAR | 77 | 61.8% | 54.5% | 0.579 |
| SUPPORTED | 63 | 53.6% | 58.7% | 0.561 |
| OUT_OF_SCOPE | 16 | 35.3% | 37.5% | 0.364 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE |
|---|---|---|---|---|
| VIOLATION | 0 | 1 | 1 | 0 |
| UNCLEAR | 3 | 42 | 28 | 4 |
| SUPPORTED | 0 | 19 | 37 | 7 |
| OUT_OF_SCOPE | 1 | 6 | 3 | 6 |

## 4. 합성 클레임 제외 ("○○ 제품은 ~" 형식을 합성으로 추정해 제외)

- 클레임 수: **571**
- 정확도 (Accuracy): **63.9%**
- Macro F1: **0.529**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 3 | 100.0% | 33.3% | 0.500 |
| OVERCLAIM | 1 | 0.0% | 0.0% | 0.000 |
| UNCLEAR | 174 | 51.6% | 54.6% | 0.531 |
| SUPPORTED | 281 | 72.2% | 76.9% | 0.745 |
| OUT_OF_SCOPE | 88 | 50.0% | 33.0% | 0.397 |
| DISCLAIMER | 24 | 100.0% | 100.0% | 1.000 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 1 | 0 | 1 | 1 | 0 | 0 |
| OVERCLAIM | 0 | 0 | 0 | 0 | 1 | 0 |
| UNCLEAR | 0 | 3 | 95 | 59 | 17 | 0 |
| SUPPORTED | 0 | 1 | 53 | 216 | 11 | 0 |
| OUT_OF_SCOPE | 0 | 1 | 35 | 23 | 29 | 0 |
| DISCLAIMER | 0 | 0 | 0 | 0 | 0 | 24 |

## 5. 자주 틀린 경우

| 정답 | 예측 | 개수 |
|---|---|---|
| UNCLEAR | SUPPORTED | 59 |
| SUPPORTED | UNCLEAR | 53 |
| OUT_OF_SCOPE | UNCLEAR | 35 |
| OUT_OF_SCOPE | SUPPORTED | 23 |
| UNCLEAR | OUT_OF_SCOPE | 17 |
| SUPPORTED | OUT_OF_SCOPE | 11 |
| UNCLEAR | OVERCLAIM | 3 |
| VIOLATION | SUPPORTED | 1 |
| SUPPORTED | OVERCLAIM | 1 |
| OVERCLAIM | OUT_OF_SCOPE | 1 |
