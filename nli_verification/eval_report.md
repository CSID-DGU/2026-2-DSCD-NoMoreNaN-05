# Mechanism B 평가 결과

- 예측 파일: `eval_verdicts_mechanism_b.json` / 정답 파일: `claims_with_db_labeled.json`
- 평가 대상: 정답 파일에서 claim_type에 EFFECT가 들어 있는 클레임 681개
- 예측이 없는 클레임: 0개

## 1. 전체 (EFFECT 포함 클레임)

- 클레임 수: **681**
- 정확도 (Accuracy): **59.8%**
- Macro F1: **0.625**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 47 | 100.0% | 78.7% | 0.881 |
| OVERCLAIM | 66 | 76.0% | 57.6% | 0.655 |
| UNCLEAR | 174 | 38.4% | 64.9% | 0.483 |
| SUPPORTED | 281 | 81.3% | 63.3% | 0.712 |
| OUT_OF_SCOPE | 88 | 42.0% | 33.0% | 0.369 |
| DISCLAIMER | 25 | 100.0% | 48.0% | 0.649 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 37 | 1 | 7 | 0 | 2 | 0 |
| OVERCLAIM | 0 | 38 | 25 | 0 | 3 | 0 |
| UNCLEAR | 0 | 11 | 113 | 29 | 21 | 0 |
| SUPPORTED | 0 | 0 | 92 | 178 | 11 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 47 | 12 | 29 | 0 |
| DISCLAIMER | 0 | 0 | 10 | 0 | 3 | 12 |

## 2. EFFECT만 있는 클레임

- 클레임 수: **523**
- 정확도 (Accuracy): **62.1%**
- Macro F1: **0.637**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 45 | 100.0% | 82.2% | 0.902 |
| OVERCLAIM | 66 | 88.4% | 57.6% | 0.697 |
| UNCLEAR | 97 | 31.1% | 67.0% | 0.425 |
| SUPPORTED | 218 | 86.2% | 68.8% | 0.765 |
| OUT_OF_SCOPE | 72 | 47.9% | 31.9% | 0.383 |
| DISCLAIMER | 25 | 100.0% | 48.0% | 0.649 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 37 | 0 | 6 | 0 | 2 | 0 |
| OVERCLAIM | 0 | 38 | 25 | 0 | 3 | 0 |
| UNCLEAR | 0 | 5 | 65 | 14 | 13 | 0 |
| SUPPORTED | 0 | 0 | 64 | 150 | 4 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 39 | 10 | 23 | 0 |
| DISCLAIMER | 0 | 0 | 10 | 0 | 3 | 12 |

## 3. 여러 유형이 함께 있는 클레임 (예: EFFECT + QUANTITY)

- 클레임 수: **158**
- 정확도 (Accuracy): **51.9%**
- Macro F1: **0.359**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 2 | 0.0% | 0.0% | 0.000 |
| UNCLEAR | 77 | 56.5% | 62.3% | 0.593 |
| SUPPORTED | 63 | 62.2% | 44.4% | 0.519 |
| OUT_OF_SCOPE | 16 | 28.6% | 37.5% | 0.324 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE |
|---|---|---|---|---|
| VIOLATION | 1 | 1 | 0 | 0 |
| UNCLEAR | 6 | 48 | 15 | 8 |
| SUPPORTED | 0 | 28 | 28 | 7 |
| OUT_OF_SCOPE | 0 | 8 | 2 | 6 |

## 4. 합성 클레임 제외 ("○○ 제품은 ~" 형식을 합성으로 추정해 제외)

- 클레임 수: **571**
- 정확도 (Accuracy): **58.0%**
- Macro F1: **0.373**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 3 | 0.0% | 0.0% | 0.000 |
| OVERCLAIM | 1 | 0.0% | 0.0% | 0.000 |
| UNCLEAR | 174 | 42.8% | 64.9% | 0.516 |
| SUPPORTED | 281 | 81.3% | 63.3% | 0.712 |
| OUT_OF_SCOPE | 88 | 44.6% | 33.0% | 0.379 |
| DISCLAIMER | 24 | 100.0% | 45.8% | 0.629 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|
| VIOLATION | 1 | 2 | 0 | 0 | 0 |
| OVERCLAIM | 0 | 0 | 0 | 1 | 0 |
| UNCLEAR | 11 | 113 | 29 | 21 | 0 |
| SUPPORTED | 0 | 92 | 178 | 11 | 0 |
| OUT_OF_SCOPE | 0 | 47 | 12 | 29 | 0 |
| DISCLAIMER | 0 | 10 | 0 | 3 | 11 |

## 5. 자주 틀린 경우

| 정답 | 예측 | 개수 |
|---|---|---|
| SUPPORTED | UNCLEAR | 92 |
| OUT_OF_SCOPE | UNCLEAR | 47 |
| UNCLEAR | SUPPORTED | 29 |
| OVERCLAIM | UNCLEAR | 25 |
| UNCLEAR | OUT_OF_SCOPE | 21 |
| OUT_OF_SCOPE | SUPPORTED | 12 |
| SUPPORTED | OUT_OF_SCOPE | 11 |
| UNCLEAR | OVERCLAIM | 11 |
| DISCLAIMER | UNCLEAR | 10 |
| VIOLATION | UNCLEAR | 7 |
