# Mechanism B 결과 전달 (EFFECT 클레임 판정)

## 1. 보내는 파일

| 파일 | 내용 |
|---|---|
| `eval_verdicts_mechanism_b.json` | 정답 데이터(영상 100개)의 EFFECT 클레임 **681개** 판정 결과 |
| `effect_all_verdicts_mechanism_b.json` | 전체 데이터(영상 535개)의 EFFECT 클레임 **1,326개** 판정 결과 (현재 규칙으로 다시 만든 것) |
| `nli.zip` | Mechanism B 코드 전체 (직접 돌릴 때) |

## 2. 합치는 방법

- 클레임 1개 = 레코드 1개 (`results` 배열)
- 키: **`video_id` + `claim_id`** (같은 영상에 같은 claim_id가 여러 제품에 붙으면 `product_ref`까지)
- 대상: `claim_type`에 **EFFECT가 들어 있는** 클레임만 (배열이면 EFFECT 포함 여부로 판단)
- `claim_type`이 여러 개인 클레임(예: EFFECT + QUANTITY)은 B가 **효능 부분만** 판정함. A 결과와 함께 있으면 우선순위로 대표 라벨 결정
- 대표 라벨 우선순위: **DISCLAIMER 먼저**, 나머지는 VIOLATION > OVERCLAIM > UNCLEAR > SUPPORTED > OUT_OF_SCOPE
- 면책 문구는 A와 B가 각자 판정함. A의 DISCLAIMER가 있으면 A 결과를 우선하면 됨

## 3. 레코드 필드

| 필드 | 뜻 |
|---|---|
| `video_id`, `product_ref`, `claim_id` | 합치기용 키 |
| `claim_type` | 입력 파일의 claim_type 그대로 (배열) |
| `text` | 광고 원문 |
| `mechanism` | 항상 `B` |
| `label` | 최종 라벨 (6개 중 하나) |
| `reason_code`, `reason` | 사유 코드와 설명 |
| `evidence_text` | 판정 근거가 된 식약처 문장 (없으면 null) |
| `scores.E` | 식약처 기능성 → 광고, 같은 말일 확률 |
| `scores.C` | 식약처 주의사항 → 광고, 반대되는 말일 확률 |
| `scores.reverse_E` | 광고 → 식약처 기능성, 같은 말일 확률 |
| `all_findings` | 대표 라벨을 정하기 전 모든 검사 결과 |
| `flags` | 질문 여부, 과장 표현 (참고용) |
| `parts` | 여러 효능을 나눠 판정한 경우 부분별 결과 |
| `duplicate_of` | 같은 영상·제품 안의 같은 문장이면 처음 클레임 ID |

## 4. 라벨 조건 (현재 규칙)

| 라벨 | 조건 |
|---|---|
| DISCLAIMER | 면책·고지 문구 ("제품과 관련 없는 내용입니다", "적절한 운동, 식이조절과 함께" 등) |
| VIOLATION | 질병·의약품 표현 ("○○을 치료한다", "○○약을 대신할 수 있다", 질병·의약품 문장 3개 모두 일치) / 같은 대상·상황의 주의사항과 충돌 ("수유부도 먹을 수 있다" 등) |
| OVERCLAIM | 인정 기능성으로 뒷받침되지 않는 효과·기간·크기를 과장 ("2주 만에", "두 배", "확실히", "깨끗이" 등) / 인정 기능성과 같은 효능을 더 크게 말함 |
| UNCLEAR | 인정 기능성 중 같은 내용 없음 / 시험·측정 결과 ("인체적용시험 결과", "~배 증가 확인") / 판단 애매 / 원료 애매 / 질문 |
| SUPPORTED | 인정 기능성과 같은 말 / 광고가 인정 기능성을 포함하고 더 말하는 내용 없음 / 여러 효능을 나눠 모두 부합 |
| OUT_OF_SCOPE | 건강 효과를 말하지 않는 문장 (구호·제형 설명 등) |

## 5. 정답 데이터 평가 결과 (681개)

| 구분 | 정확도 | Macro F1 |
|---|---|---|
| 전체 | 69.8% | 0.768 |
| EFFECT만 있는 클레임 (523) | 74.6% | 0.781 |
| 여러 유형이 함께 있는 클레임 (158) | 53.8% | 0.376 |

| 라벨 | 정밀도 | 재현율 | F1 |
|---|---|---|---|
| VIOLATION | 100.0% | 95.7% | 0.978 |
| OVERCLAIM | 92.9% | 98.5% | 0.956 |
| UNCLEAR | 51.6% | 54.6% | 0.531 |
| SUPPORTED | 72.2% | 76.9% | 0.745 |
| OUT_OF_SCOPE | 50.0% | 33.0% | 0.397 |
| DISCLAIMER | 100.0% | 100.0% | 1.000 |

- 판정 규칙은 이 정답 데이터의 오류를 보며 보완함 (정답을 보기 전 규칙의 정확도는 59.8%)
- 모델: `Huffon/klue-roberta-base-nli` (추가 학습 없이 사용)

## 6. 사유 코드

| 코드 | 뜻 |
|---|---|
| `DISEASE_CLAIM` | 질병 예방·치료 효과를 말함 (질병 표현 문장 3개 모두 일치) |
| `DRUG_CLAIM` | 의약품을 대신하거나 약효를 높인다고 말함 (의약품 표현 문장 3개 모두 일치) |
| `PRECAUTION_CONFLICT` | 식약처 주의사항과 반대되는 내용 |
| `MULTI_EFFECT` | 여러 효능을 한 문장에 담음 (효능별로 나눠서 확인 필요) |
| `SAME_TOPIC` | 인정 기능성과 같은 주제지만 같은 말인지 확인 필요 (광고 → 식약처만 성립) |
| `TRIAL_RESULT` | 시험·측정 결과를 말함 (인정 범위 안인지 문구만으로 확인 어려움) |
| `IMPLIES_RECOGNIZED` | 광고가 인정 기능성을 포함하고 더 말하는 내용이 없음 (광고 → 식약처 성립) |
| `EXAGGERATION_NO_EVIDENCE` | 인정 근거가 없는 효과·기간·크기를 과장 표현으로 말함 |
| `PART_SAME_TOPIC` | 나눈 효능 중 일부가 인정 기능성과 같은 주제지만 같은 말인지 확인 필요 |
| `ALL_PARTS_SUPPORTED` | 여러 효능을 나눠 비교한 결과 모두 인정 기능성과 같은 내용 |
| `PART_STRONGER_THAN_RECOGNIZED` | 나눈 효능 중 일부가 인정 범위보다 크게 말함 |
| `PART_NO_MATCHING_EVIDENCE` | 나눈 효능 중 일부가 인정 기능성에 없음 |
| `PART_LOW_CONFIDENCE` | 나눈 효능 중 일부의 판단이 애매함 |
| `STRONGER_THAN_RECOGNIZED` | 인정 기능성과 같은 효능을 인정 범위보다 크게 말함 (광고 → 식약처 방향 E ≥ 0.9) |
| `NO_MATCHING_EVIDENCE` | 식약처 인정 기능성 중 같은 내용이 없음 |
| `LOW_CONFIDENCE` | 모델 판단이 애매함 |
| `QUESTION` | 질문 문장이라 주장으로 보기 어려움 |
| `DISEASE_DRUG_UNCERTAIN` | 질병·의약품 표현일 가능성 (표현 문장 3개 중 2개 일치) |
| `PRODUCT_UNRESOLVED` | 광고 제품을 식약처 DB에서 확정하지 못함 |
| `NO_PRODUCT_TEXT` | 제품의 기능성 문장이 없음 |
| `INGREDIENT_NOT_IN_PRODUCT` | 광고가 말하는 원료가 제품 기능성에 없거나 애매함 |
| `TARGET_UNRESOLVED` | 광고가 무엇에 대해 말하는지 알 수 없음 |
| `FUNCTION` | 식약처 인정 기능성과 같은 내용 |
| `NOT_HEALTH_CLAIM` | 건강 효과를 말하는 문장이 아님 |
| `DISCLAIMER` | 광고 속 면책·고지 문구 (주장이 아님) |
