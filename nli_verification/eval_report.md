# Mechanism B 평가 결과

- 예측 파일: `eval_verdicts_mechanism_b.json` / 정답 파일: `claims_with_db_labeled.json`
- 평가 대상: 정답 파일에서 claim_type에 EFFECT가 들어 있는 클레임 681개
- 예측이 없는 클레임: 0개

## 1. 전체 (EFFECT 포함 클레임)

- 클레임 수: **681**
- 정확도 (Accuracy): **65.6%**
- Macro F1: **0.716**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 47 | 100.0% | 91.5% | 0.956 |
| OVERCLAIM | 66 | 69.7% | 93.9% | 0.800 |
| UNCLEAR | 174 | 44.5% | 42.0% | 0.432 |
| SUPPORTED | 281 | 73.2% | 76.9% | 0.750 |
| OUT_OF_SCOPE | 88 | 43.9% | 33.0% | 0.377 |
| DISCLAIMER | 25 | 100.0% | 96.0% | 0.980 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 43 | 1 | 1 | 0 | 2 | 0 |
| OVERCLAIM | 0 | 62 | 1 | 0 | 3 | 0 |
| UNCLEAR | 0 | 24 | 73 | 56 | 21 | 0 |
| SUPPORTED | 0 | 1 | 53 | 216 | 11 | 0 |
| OUT_OF_SCOPE | 0 | 1 | 35 | 23 | 29 | 0 |
| DISCLAIMER | 0 | 0 | 1 | 0 | 0 | 24 |

## 2. EFFECT만 있는 클레임

- 클레임 수: **523**
- 정확도 (Accuracy): **72.3%**
- Macro F1: **0.750**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 45 | 100.0% | 95.6% | 0.977 |
| OVERCLAIM | 66 | 86.1% | 93.9% | 0.899 |
| UNCLEAR | 97 | 42.0% | 48.5% | 0.450 |
| SUPPORTED | 218 | 78.9% | 82.1% | 0.804 |
| OUT_OF_SCOPE | 72 | 51.1% | 31.9% | 0.393 |
| DISCLAIMER | 25 | 100.0% | 96.0% | 0.980 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 43 | 0 | 0 | 0 | 2 | 0 |
| OVERCLAIM | 0 | 62 | 1 | 0 | 3 | 0 |
| UNCLEAR | 0 | 9 | 47 | 28 | 13 | 0 |
| SUPPORTED | 0 | 1 | 34 | 179 | 4 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 29 | 20 | 23 | 0 |
| DISCLAIMER | 0 | 0 | 1 | 0 | 0 | 24 |

## 3. 여러 유형이 함께 있는 클레임 (예: EFFECT + QUANTITY)

- 클레임 수: **158**
- 정확도 (Accuracy): **43.7%**
- Macro F1: **0.323**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 2 | 0.0% | 0.0% | 0.000 |
| UNCLEAR | 77 | 50.0% | 33.8% | 0.403 |
| SUPPORTED | 63 | 54.4% | 58.7% | 0.565 |
| OUT_OF_SCOPE | 16 | 28.6% | 37.5% | 0.324 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE |
|---|---|---|---|---|
| VIOLATION | 1 | 1 | 0 | 0 |
| UNCLEAR | 15 | 26 | 28 | 8 |
| SUPPORTED | 0 | 19 | 37 | 7 |
| OUT_OF_SCOPE | 1 | 6 | 3 | 6 |

## 4. 합성 클레임 제외 ("○○ 제품은 ~" 형식을 합성으로 추정해 제외)

- 클레임 수: **571**
- 정확도 (Accuracy): **59.9%**
- Macro F1: **0.508**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 3 | 100.0% | 33.3% | 0.500 |
| OVERCLAIM | 1 | 0.0% | 0.0% | 0.000 |
| UNCLEAR | 174 | 44.8% | 42.0% | 0.433 |
| SUPPORTED | 281 | 73.2% | 76.9% | 0.750 |
| OUT_OF_SCOPE | 88 | 46.8% | 33.0% | 0.387 |
| DISCLAIMER | 24 | 100.0% | 95.8% | 0.979 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 1 | 1 | 1 | 0 | 0 | 0 |
| OVERCLAIM | 0 | 0 | 0 | 0 | 1 | 0 |
| UNCLEAR | 0 | 24 | 73 | 56 | 21 | 0 |
| SUPPORTED | 0 | 1 | 53 | 216 | 11 | 0 |
| OUT_OF_SCOPE | 0 | 1 | 35 | 23 | 29 | 0 |
| DISCLAIMER | 0 | 0 | 1 | 0 | 0 | 23 |

## 5. 자주 틀린 경우

| 정답 | 예측 | 개수 |
|---|---|---|
| UNCLEAR | SUPPORTED | 56 |
| SUPPORTED | UNCLEAR | 53 |
| OUT_OF_SCOPE | UNCLEAR | 35 |
| UNCLEAR | OVERCLAIM | 24 |
| OUT_OF_SCOPE | SUPPORTED | 23 |
| UNCLEAR | OUT_OF_SCOPE | 21 |
| SUPPORTED | OUT_OF_SCOPE | 11 |
| OVERCLAIM | OUT_OF_SCOPE | 3 |
| VIOLATION | OUT_OF_SCOPE | 2 |
| VIOLATION | OVERCLAIM | 1 |
