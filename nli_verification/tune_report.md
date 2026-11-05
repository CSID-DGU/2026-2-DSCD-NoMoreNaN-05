# Mechanism B 조정 결과

- 클레임 수: 681 (EFFECT 포함)
- 방법: 기준값·규칙 탐색: hi=0.5, rev=0.95, need_sig=True, num_sig=False, sig_only=True, tmpl=0.5, tmpl_mean=0.7, st_sup=True

| | 정확도 | Macro F1 |
|---|---|---|
| 조정 전 | 65.6% | 0.716 |
| 조정 후 | 67.3% | 0.720 |

## 조정 전

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

## 조정 후

- 클레임 수: **681**
- 정확도 (Accuracy): **67.3%**
- Macro F1: **0.720**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 47 | 95.6% | 91.5% | 0.935 |
| OVERCLAIM | 66 | 70.0% | 95.5% | 0.808 |
| UNCLEAR | 174 | 48.0% | 42.0% | 0.448 |
| SUPPORTED | 281 | 74.3% | 80.4% | 0.773 |
| OUT_OF_SCOPE | 88 | 43.9% | 33.0% | 0.377 |
| DISCLAIMER | 25 | 100.0% | 96.0% | 0.980 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 43 | 1 | 0 | 1 | 2 | 0 |
| OVERCLAIM | 0 | 63 | 0 | 0 | 3 | 0 |
| UNCLEAR | 1 | 24 | 73 | 55 | 21 | 0 |
| SUPPORTED | 0 | 1 | 43 | 226 | 11 | 0 |
| OUT_OF_SCOPE | 1 | 1 | 35 | 22 | 29 | 0 |
| DISCLAIMER | 0 | 0 | 1 | 0 | 0 | 24 |

