# Mechanism B 조정 결과

- 클레임 수: 681 (EFFECT 포함)
- 방법: 기준값·규칙 탐색: hi=0.5, rev=0.7, need_sig=True, num_sig=False, sig_only=True, tmpl=0.5, tmpl_mean=0.7, st_sup=True

| | 정확도 | Macro F1 |
|---|---|---|
| 조정 전 | 69.8% | 0.768 |
| 조정 후 | 71.5% | 0.772 |

## 조정 전

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

## 조정 후

- 클레임 수: **681**
- 정확도 (Accuracy): **71.5%**
- Macro F1: **0.772**

| 정답 라벨 | 개수 | 정밀도 | 재현율 | F1 |
|---|---|---|---|---|
| VIOLATION | 47 | 95.7% | 95.7% | 0.957 |
| OVERCLAIM | 66 | 92.9% | 98.5% | 0.956 |
| UNCLEAR | 174 | 56.4% | 53.4% | 0.549 |
| SUPPORTED | 281 | 72.8% | 81.9% | 0.771 |
| OUT_OF_SCOPE | 88 | 50.0% | 33.0% | 0.397 |
| DISCLAIMER | 25 | 100.0% | 100.0% | 1.000 |

**혼동 행렬** (행 = 정답, 열 = 예측)

| 정답 \ 예측 | VIOLATION | OVERCLAIM | UNCLEAR | SUPPORTED | OUT_OF_SCOPE | DISCLAIMER |
|---|---|---|---|---|---|---|
| VIOLATION | 45 | 0 | 0 | 2 | 0 | 0 |
| OVERCLAIM | 0 | 65 | 0 | 0 | 1 | 0 |
| UNCLEAR | 1 | 3 | 93 | 60 | 17 | 0 |
| SUPPORTED | 0 | 1 | 39 | 230 | 11 | 0 |
| OUT_OF_SCOPE | 1 | 1 | 33 | 24 | 29 | 0 |
| DISCLAIMER | 0 | 0 | 0 | 0 | 0 | 25 |

