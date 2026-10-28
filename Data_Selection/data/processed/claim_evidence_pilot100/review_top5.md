# Claim 100개 Evidence 순위 검토

실제 BGE-reranker-v2-m3 점수. sigmoid(logit)은 관련성 점수이며 참·거짓 확률이 아닙니다.
제품명 유사도 80점과 별개입니다. 관련성 임계값 없이 정렬했으므로 낮은 관련성의 자료도 포함될 수 있습니다.
원료 자료는 제품 함유를 입증하지 않습니다. 세부 항목별 충분성과 최종 판정은 아직 미평가입니다.

- Claim: 100개
- 후보 있음: 84개 / 후보 없음: 16개

| K | 전달되는 근거 연결 수 | 후보가 K개 이상인 Claim 수 |
| ---: | ---: | ---: |
| 1 | 84 | 84 |
| 3 | 252 | 84 |
| 5 | 416 | 82 |
| 10 | 810 | 75 |

## db_001_AKyDb1Yhaio / c01

- 영상: https://www.youtube.com/watch?v=AKyDb1Yhaio
- 제품명: BNS 혈당엔 바나바
- 제품 식별: matched
- Claim: **바나바잎 추출물 + 아연 + 비타민B1**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=1531
- 전체 후보: 21개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.996797 | product_direct | BNS혈당엔바나바 | 6. 비타민 B1 : 표시량[5mg/500mg]의 80~180% | products:1531/specification@113:148 |
| 2 | 0.996269 | product_direct | BNS혈당엔바나바 | 비타민B1 _ (1) 탄수화물과 에너지 대사에 필요 | products:1531/main_functionality@71:99 |
| 3 | 0.99557 | product_direct | BNS혈당엔바나바 | 비타민B1 _ (1) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 | products:1531/intake_precautions@0:41 |
| 4 | 0.995073 | product_direct | BNS혈당엔바나바 | 1일 1회, 1회 1정을 물과 함께 섭취하십시오. | products:1531/intake_method@0:27 |
| 5 | 0.993631 | product_direct | BNS혈당엔바나바 | 바나바잎추출물 _  ①식후 혈당상승 억제에 도움을 줄 수 있음 | products:1531/main_functionality@0:34 |

## db_003_VABlVWjX9t4 / c02

- 영상: https://www.youtube.com/watch?v=VABlVWjX9t4
- 제품명: G4000 프로바이오틱스
- 제품 식별: matched
- Claim: **식약처가 인증한 십구 종의 생유산균을 함유하여**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=2228
- 전체 후보: 26개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.424511 | product_direct | G4000 프로바이오틱스 | [프로바이오틱스] | products:2228/intake_precautions@0:9 |
| 2 | 0.368165 | product_direct | G4000 프로바이오틱스 | [프로바이오틱스] | products:2228/main_functionality@0:9 |
| 3 | 0.354971 | product_direct | G4000 프로바이오틱스 | 1일 1회, 1회 1포(2 g)를 섭취한다. | products:2228/intake_method@0:24 |
| 4 | 0.2771 | product_direct | G4000 프로바이오틱스 | (라) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 | products:2228/intake_precautions@117:150 |
| 5 | 0.262787 | product_direct | G4000 프로바이오틱스 | (가) 질환이 있거나 의약품 복용 시 전문가와 상담할 것 | products:2228/intake_precautions@10:41 |

## db_004_dqks_z0q9Go / c03

- 영상: https://www.youtube.com/watch?v=dqks_z0q9Go
- 제품명: 간건강 더하기 밀크씨슬 비타민B군
- 제품 식별: unmatched
- Claim: **건강기능식품**
- 식별 경로/사유: exact_name / multiple_candidates; product_id=None
- 전체 후보: 54개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.325111 | ingredient_reference | 밀크씨슬 추출물(Milk Thistle Extract) | 간 건강에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:609 |
| 2 | 0.2935 | ingredient_reference | 밀크씨슬 추출물(Milk Thistle Extract) | 간 건강에 도움을 줄 수 있음(기타기능II) | evidence:1098 |
| 3 | 0.262498 | ingredient_reference | 밀크씨슬추출물 | “간 건강에 도움을 줄 수 있음” (기타기능II) | evidence:1191 |
| 4 | 0.262498 | ingredient_reference | 밀크씨슬추출물 | “간 건강에 도움을 줄 수 있음” (기타기능II) | evidence:1222 |
| 5 | 0.262498 | ingredient_reference | 밀크씨슬추출물 | “간 건강에 도움을 줄 수 있음” (기타기능II) | evidence:1333 |

## db_006_oUr4voFFuBo / c14

- 영상: https://www.youtube.com/watch?v=oUr4voFFuBo
- 제품명: 배한호 원장 감비책 다이어트
- 제품 식별: unmatched
- Claim: **혈중 중성지질 개선에 도움을 줄 수 있음**
- 식별 경로/사유: full_name_damerau_levenshtein / manufacturer_missing_for_typo_route; product_id=None
- 전체 후보: 15개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.802497 | ingredient_reference | 난소화성말토덱스트린 | 혈중 중성지질 개선에 도움을 줄 수 있음(기타기능 II) | evidence:250 |
| 2 | 0.671324 | ingredient_reference | 난소화성말토덱스트린 | "난소화성말토덱스트린은 식사와 함께 섭취하면 당의 흡수를 억제시켜 식후 혈당 조절에 도움을 줄 수 있습니다."  ◆ 인체시험에서 난소화성말토덱스트린을 식사와 함께 섭취할 경우 당의 흡수를 억제시켜 식후 혈당 조절에 도움을 줄 수 있음을 확인하였으나 자료의 수가 제한되어 있음. 따라서 반드시 ‘---에 도움을 줄 수 있습니다’의 형식으로 표시하여야 함. | evidence:317 |
| 3 | 0.184341 | ingredient_reference | 난소화성말토덱스트린 | 건강기능식품공전 II.2.4.4.4 난소화성말토덱스트린과 동일 | evidence:252 |
| 4 | 0.103261 | ingredient_reference | 난소화성말토덱스트린 | ◆ 난소화성말토덱스트린은 당뇨병의 치료 및 예방에 사용될 수 없으므로 당뇨병 치료가 필요한 경우에는 의사와 상담 하에 사용하여야 합니다. | evidence:319 |
| 5 | 0.0987294 | ingredient_reference | 난소화성말토덱스트린 | ‘난소화성말토덱스트린’로서 | evidence:318 |

## db_010_cQZBp9O3Blk / c17

- 영상: https://www.youtube.com/watch?v=cQZBp9O3Blk
- 제품명: 고려은단 멀티비타민 올인원
- 제품 식별: matched
- Claim: **vit E**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=5216
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.804455 | product_direct | 고려은단 멀티비타민 올인원 | 4) 비타민E: 표시량(5 mg α-TE/ 1560 mg)의 80 ~ 150% | products:5216/specification@132:175 |
| 2 | 0.77859 | product_direct | 고려은단 멀티비타민 올인원 | [비타민E] 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요 | products:5216/main_functionality@139:177 |
| 3 | 0.416829 | product_direct | 고려은단 멀티비타민 올인원 | 1일 1회, 1회 1정(1.56 g)을 물과 함께 섭취하십시오. | products:5216/intake_method@0:35 |
| 4 | 0.402582 | product_direct | 고려은단 멀티비타민 올인원 | 16) 마그네슘: 표시량(104 mg/ 1560 mg)의 80 ~ 150% | products:5216/specification@632:673 |
| 5 | 0.40071 | product_direct | 고려은단 멀티비타민 올인원 | [비타민D] ①칼슘과 인이 흡수되고 이용되는데 필요 ②뼈의 형성과 유지에 필요 ③골다공증발생 위험 감소에 도움을 줌 | products:5216/main_functionality@74:138 |

## db_011_8OrRhb8sQnw / c09

- 영상: https://www.youtube.com/watch?v=8OrRhb8sQnw
- 제품명: 고려은단 멀티비타민 올인원 우먼
- 제품 식별: matched
- Claim: **비타민13종 미네랄10종**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=5219
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.477358 | product_direct | 고려은단 멀티비타민 올인원 우먼 | [칼슘] ①뼈와 치아 형성에 필요 ②신경과 근육 기능 유지에 필요 ③정상적인 혈액응고에 필요 ④골다공증발생 위험 감소에 도움을 줌 | products:5219/main_functionality@570:642 |
| 2 | 0.464507 | product_direct | 고려은단 멀티비타민 올인원 우먼 | 1) 성상: 고유의 향미가 있고 이미, 이취가 없는 연한 자줏빛 분홍색의 장방형 코팅정제 | products:5219/specification@0:49 |
| 3 | 0.434367 | product_direct | 고려은단 멀티비타민 올인원 우먼 | [엽산] ①세포와 혈액생성에 필요 ②태아 신경관의 정상 발달에 필요 ③혈액의 호모시스테인 수준을 정상으로 유지하는데 필요 | products:5219/main_functionality@373:440 |
| 4 | 0.414646 | product_direct | 고려은단 멀티비타민 올인원 우먼 | 고유의 향미가 있고 이미, 이취가 없는 연한 자줏빛 분홍색의 장방형 코팅정제 | products:5219/appearance@0:42 |
| 5 | 0.373832 | product_direct | 고려은단 멀티비타민 올인원 우먼 | [요오드] ①갑상선 호르몬의 합성에 필요 ②에너지 생성에 필요 ③신경발달에 필요 | products:5219/main_functionality@820:864 |

## db_013_NrsycE3cMV8 / c10

- 영상: https://www.youtube.com/watch?v=NrsycE3cMV8
- 제품명: 고려은단 코엔자임Q10
- 제품 식별: matched
- Claim: **목넘김이 편한 미니 사이즈**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=5239
- 전체 후보: 23개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.0810396 | product_direct | 고려은단 코엔자임Q10 | 20250602 | products:5239/registration_date@0:8 |
| 2 | 0.0797101 | product_direct | 고려은단 코엔자임Q10 | (주)서흥 | products:5239/company_name@0:5 |
| 3 | 0.0615456 | product_direct | 고려은단 코엔자임Q10 | (2) 코엔자임Q10 : 표시량(100 mg/0.25g)의 80%~120% | products:5239/specification@65:106 |
| 4 | 0.0517057 | product_direct | 고려은단 코엔자임Q10 | 고유의 향미가 있고 이미, 이취가 없는 주황색의 점도가 있는 내용물을 함유한 빨간색 타원형 연질캡슐 | products:5239/appearance@0:55 |
| 5 | 0.0492149 | product_direct | 고려은단 코엔자임Q10 | (1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 주황색의 점도가 있는 내용물을 함유한 빨간색 타원형 연질캡슐 | products:5239/specification@0:64 |

## db_014_E5uL0UwVQsQ / c07

- 영상: https://www.youtube.com/watch?v=E5uL0UwVQsQ
- 제품명: 고려은단 비타민C 골드 프리미엄
- 제품 식별: unmatched
- Claim: **건강기능식품 광고입니다**
- 식별 경로/사유: full_name_damerau_levenshtein / manufacturer_missing_for_typo_route; product_id=None

**연결 가능한 Evidence 없음**

## db_016_hgr3QrFdKqk / c01

- 영상: https://www.youtube.com/watch?v=hgr3QrFdKqk
- 제품명: 고려은단 비타민C1000
- 제품 식별: matched
- Claim: **유럽산 옥수수로 만든 영국산 비타민C**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=5247
- 전체 후보: 14개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.572893 | product_direct | 고려은단비타민C1000 | 2. 비타민C : 표시량(1,000mg/1,080mg)의 80~150%이어야 한다. | products:5247/specification@41:87 |
| 2 | 0.463912 | product_direct | 고려은단비타민C1000 | 1일 1회, 1회 1정(1,080mg)을 식사 후 먹는물로 섭취합니다. | products:5247/intake_method@0:39 |
| 3 | 0.36188 | product_direct | 고려은단비타민C1000 | ①결합조직 형성과 기능유지에 필요②철의 흡수에 필요③항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요 | products:5247/main_functionality@0:60 |
| 4 | 0.322334 | product_direct | 고려은단비타민C1000 | 1. 성상 : 고유의 향미가 있고, 이미·이취가 없는 백색의 장방형 정제 | products:5247/specification@0:40 |
| 5 | 0.319045 | product_direct | 고려은단비타민C1000 | 202100108172 | products:5247/manufacturing_report_number@0:12 |

## db_017_ibzN_kNSftI / c08

- 영상: https://www.youtube.com/watch?v=ibzN_kNSftI
- 제품명: 고려은단 비타민C1000
- 제품 식별: matched
- Claim: **유통기한 확인하여 식품선택 올바르게**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=5247
- 전체 후보: 14개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.751727 | product_direct | 고려은단비타민C1000 | 제조일로부터 36개월 | products:5247/shelf_life@0:11 |
| 2 | 0.352707 | product_direct | 고려은단비타민C1000 | 20220726 | products:5247/registration_date@0:8 |
| 3 | 0.229411 | product_direct | 고려은단비타민C1000 | 1. 성상 : 고유의 향미가 있고, 이미·이취가 없는 백색의 장방형 정제 | products:5247/specification@0:40 |
| 4 | 0.225972 | product_direct | 고려은단비타민C1000 | 1일 1회, 1회 1정(1,080mg)을 식사 후 먹는물로 섭취합니다. | products:5247/intake_method@0:39 |
| 5 | 0.186739 | product_direct | 고려은단비타민C1000 | 고려은단(주) | products:5247/company_name@0:7 |

## db_020_cBZk8yOvCC0 / c06

- 영상: https://www.youtube.com/watch?v=cBZk8yOvCC0
- 제품명: 옵티 MSM
- 제품 식별: matched
- Claim: **고품질 프리미엄 MSM원료 사용**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=30138
- 전체 후보: 24개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.466284 | product_direct | 옵티 MSM | 1일 1회, 1회 1포씩 충분한 물과 합께 섭취한다. | products:30138/intake_method@0:29 |
| 2 | 0.342439 | product_direct | 옵티 MSM | 2) MSM : 표시량 [2,000mg/2,200mg(1포)]의  80~120% | products:30138/specification@39:83 |
| 3 | 0.294969 | product_direct | 옵티 MSM | 5) 납 : 0.1 이하(mg/kg) | products:30138/specification@137:157 |
| 4 | 0.294277 | product_direct | 옵티 MSM | [MSM제품]① 관절 및 연골건강에 도움을 줄 수 있음 | products:30138/main_functionality@0:30 |
| 5 | 0.292022 | product_direct | 옵티 MSM | 6) 카드뮴 : 0.1 이하 (mg/kg) | products:30138/specification@159:182 |

## db_022_Y6gkveTxNxc / c03

- 영상: https://www.youtube.com/watch?v=Y6gkveTxNxc
- 제품명: 관절엔 소연골 뮤코다당단백 콘드로이친 골드
- 제품 식별: matched
- Claim: **[VAS] 무릎관절의 통증 개선 확인**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=6307
- 전체 후보: 25개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.769304 | product_direct | 관절엔 소연골 뮤코다당단백 콘드로이친 골드 | 2) 비타민D : 칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌. | products:6307/main_functionality@36:103 |
| 2 | 0.746888 | product_direct | 관절엔 소연골 뮤코다당단백 콘드로이친 골드 | 1일 2회, 1회 1정을 충분한 물과 함께 섭취하십시오. 1일 1회, 1회 2정을 충분한 물과 함께 섭취하십시오. | products:6307/intake_method@0:63 |
| 3 | 0.683802 | product_direct | 관절엔 소연골 뮤코다당단백 콘드로이친 골드 | 1) 뮤코다당·단백 : 관절 및 연골건강에 도움을 줄 수 있음. | products:6307/main_functionality@0:35 |
| 4 | 0.653788 | product_direct | 관절엔 소연골 뮤코다당단백 콘드로이친 골드 | 3) 비타민D : 표시량(10ug/2000mg)의 80~180% | products:6307/specification@88:123 |
| 5 | 0.647883 | product_direct | 관절엔 소연골 뮤코다당단백 콘드로이친 골드 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 노란 하얀색의 장방형 제피정제 | products:6307/specification@0:46 |

## db_031_7Gp4DKcVBkg / c08

- 영상: https://www.youtube.com/watch?v=7Gp4DKcVBkg
- 제품명: 관절연골엔 구절초
- 제품 식별: matched
- Claim: **개별인정형 건강기능식품**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=6407
- 전체 후보: 25개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.824653 | ingredient_reference | 구절초추출물(기능성원료인정제2021-12호) | (국문) 관절 및 연골 건강에 도움을 줄 수 있음 (영문) May help to maintain healthy joint and cartilage | evidence:2504 |
| 2 | 0.813642 | product_direct | 관절연골엔 구절초 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 회갈색의 장방형 제피정제 | products:6407/specification@0:43 |
| 3 | 0.801758 | product_direct | 관절연골엔 구절초 | 고유의 향미가 있고 이미, 이취가 없는 회갈색의 장방형 제피정제 | products:6407/appearance@0:35 |
| 4 | 0.697339 | product_direct | 관절연골엔 구절초 | (영문) May help to maintain healthy joint and cartilage | products:6407/main_functionality@28:81 |
| 5 | 0.672848 | product_direct | 관절연골엔 구절초 | 1일 1회, 1회 1정을 충분한 물과 함께 섭취하십시오. | products:6407/intake_method@0:31 |

## db_033_iemqoCEprgg / c11

- 영상: https://www.youtube.com/watch?v=iemqoCEprgg
- 제품명: 관절연골엔 구절초
- 제품 식별: matched
- Claim: **평생하나뿐인 관절연골엔 구절초**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=6407
- 전체 후보: 25개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.448788 | product_direct | 관절연골엔 구절초 | (국문) 관절 및 연골 건강에 도움을 줄 수 있음 | products:6407/main_functionality@0:27 |
| 2 | 0.432108 | product_direct | 관절연골엔 구절초 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 회갈색의 장방형 제피정제 | products:6407/specification@0:43 |
| 3 | 0.409029 | ingredient_reference | 구절초추출물(기능성원료인정제2021-12호) | (국문) 관절 및 연골 건강에 도움을 줄 수 있음 (영문) May help to maintain healthy joint and cartilage | evidence:2504 |
| 4 | 0.378608 | product_direct | 관절연골엔 구절초 | 제조일로부터 24개월 | products:6407/shelf_life@0:11 |
| 5 | 0.368468 | product_direct | 관절연골엔 구절초 | 고유의 향미가 있고 이미, 이취가 없는 회갈색의 장방형 제피정제 | products:6407/appearance@0:35 |

## db_037_GfXTXY4Cojo / c03

- 영상: https://www.youtube.com/watch?v=GfXTXY4Cojo
- 제품명: 관절연골엔 우슬 조인트100 프리미엄
- 제품 식별: unmatched
- Claim: **식약처 기능성 인정**
- 식별 경로/사유:  / conflicting_input_identity_observations; product_id=None
- 전체 후보: 6개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.762905 | ingredient_reference | 우슬 등 복합물(HL-Joint100)(기능성원료인정제2018-13호) | (국문) 관절 및 연골건강에 도움을 줄 수 있음 (영문) May help to maintain healthy joint and cartilage | evidence:2344 |
| 2 | 0.478317 | ingredient_reference | 우슬 등 복합물(HL-Joint100) | 연골 및 관절 건강에 도움을 줄 수 있음. | evidence:966 |
| 3 | 0.469773 | ingredient_reference | 우슬 등 복합물(HL-Joint100)(기능성원료인정제2018-13호) | (1) 영·유아, 어린이, 임산부 및 수유부는 섭취에 주의 (2) 에스트로겐 호르몬에 민감한 사람은 섭취에 주의 | evidence:2346 |
| 4 | 0.292113 | ingredient_reference | 우슬 등 복합물(HL-Joint100)(기능성원료인정제2018-13호) | 1,000 (mg) 1,000 (mg) | evidence:2345 |
| 5 | 0.0871983 | ingredient_reference | 우슬 등 복합물(HL-Joint100) | 석류등복합물로서 1,000mg/일 | evidence:967 |

## db_038_-56FN2YCC-I / c10

- 영상: https://www.youtube.com/watch?v=-56FN2YCC-I
- 제품명: 관절팔팔
- 제품 식별: matched
- Claim: **1일 섭취량 당 EPA, DHA, DPA, ALA 합으로 50 mg 이상 함유**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=6569
- 전체 후보: 30개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.881479 | product_direct | 관절팔팔 | 2)기능성분 docosahexanoic acid(DHA), eicosapentaenoic acid(EPA), dacosapentaenoic(DPA), a-Linolenic acid(ALA) : 합으로 50mg/620mg 이상 | products:6569/specification@59:184 |
| 2 | 0.169191 | product_direct | 관절팔팔 | (2) 간 질환이 있거나 혈전용해제 등 복용 시 전문가와 상담할 것 | products:6569/intake_precautions@25:62 |
| 3 | 0.165684 | product_direct | 관절팔팔 | 1일 2회, 1회 1캡슐을 물과 함께 섭취하십시오. | products:6569/intake_method@0:28 |
| 4 | 0.161562 | product_direct | 관절팔팔 | 3)비타민E(D-a-tocopherol) : 13.64mg/620mg의 80~150%이어야 한다 | products:6569/specification@185:238 |
| 5 | 0.149244 | product_direct | 관절팔팔 | 1) 보존기준 : 연질캡슐 특성상 보관 상태에 따라 외형 및 성상 변화가 생길 우려가 있으니 반드시 고온다습한 곳과 직사광선을 피하여 실온에 보관하십시오. 2) 어린이의 손에 닿지 않는 곳에 보관하십시오. 보관3) 소비기간 : 36개월 (건강기능식품 인정서 원료 인정서) | products:6569/storage_and_distribution_standard@0:151 |

## db_039_zptASsSd0nY / c07

- 영상: https://www.youtube.com/watch?v=zptASsSd0nY
- 제품명: 관절팔팔
- 제품 식별: unmatched
- Claim: **초록입홍합추출오일복합물**
- 식별 경로/사유:  / conflicting_input_identity_observations; product_id=None
- 전체 후보: 9개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.866839 | ingredient_reference | 초록입홍합추출오일복합물 | 관절건강에 도움이 될 수 있습니다. | evidence:119 |
| 2 | 0.8412 | ingredient_reference | 초록입홍합추출오일 | 관절건강에 도움을 줄 수 있음  (생리활성기능 2등급) | evidence:167 |
| 3 | 0.735698 | ingredient_reference | 초록입홍합추출오일복합물(기능성원료인정제2004-8호) | (국문) 관절건강에 도움이 될 수 있음 (영문) May help to maintain healthy joint | evidence:1802 |
| 4 | 0.709168 | ingredient_reference | 초록입홍합추출오일 | 초록입홍합추출오일로서 200 mg/일 | evidence:168 |
| 5 | 0.65362 | ingredient_reference | 초록입홍합추출오일 | 혈전용해제를 복용하시는 분은 의사와 상담 후 섭취 | evidence:169 |

## db_043_pqKwSu8og9A / c08

- 영상: https://www.youtube.com/watch?v=pqKwSu8og9A
- 제품명: 간 건강 프리미엄 밀크씨슬
- 제품 식별: unmatched
- Claim: **108 g(900 mg x 120정)**
- 식별 경로/사유: exact_name / multiple_candidates; product_id=None
- 전체 후보: 54개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.0817228 | ingredient_reference | 밀크씨슬 추출물(Milk Thistle Extract) | 간 건강에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:609 |
| 2 | 0.0551906 | ingredient_reference | 밀크씨슬추출물 | “간 건강에 도움을 줄 수 있음” (기타기능II) | evidence:1191 |
| 3 | 0.0551906 | ingredient_reference | 밀크씨슬추출물 | “간 건강에 도움을 줄 수 있음” (기타기능II) | evidence:1222 |
| 4 | 0.0551906 | ingredient_reference | 밀크씨슬추출물 | “간 건강에 도움을 줄 수 있음” (기타기능II) | evidence:1333 |
| 5 | 0.0551906 | ingredient_reference | 밀크씨슬추출물 | “간 건강에 도움을 줄 수 있음” (기타기능II) | evidence:1349 |

## db_045_kzP_81Cub6Y / c04

- 영상: https://www.youtube.com/watch?v=kzP_81Cub6Y
- 제품명: 뇌보
- 제품 식별: matched
- Claim: **면역력 증진 · 피로 개선 · 혈소판 응집억제를 통한 혈액 흐름 · 기억력 개선 · 항산화에 도움을 줄 수 있음**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=8341
- 전체 후보: 22개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.944676 | product_direct | 뇌보 | ①면역력 증진·피로개선에 도움을 줄 수 있음 | products:8341/main_functionality@0:24 |
| 2 | 0.892509 | product_direct | 뇌보 | ②혈소판 응집억제를 통한 혈액흐름·기억력 개선·항산화에 도움을 줄 수 있음 | products:8341/main_functionality@27:68 |
| 3 | 0.599069 | ingredient_reference | 홍삼 | 혈당 조절에 도움을 줄 수 있음 | evidence:1557 |
| 4 | 0.534036 | ingredient_reference | 홍삼(제2024-20호) | 23 (mg/일) 23 (mg/일) | evidence:2799 |
| 5 | 0.437399 | ingredient_reference | 홍삼 | 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 22~80mg | evidence:1558 |

## db_046_MWx5nDT8pDk / c07

- 영상: https://www.youtube.com/watch?v=MWx5nDT8pDk
- 제품명: 눈건강 루테인 골드
- 제품 식별: matched
- Claim: **건강기능식품**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=8442
- 전체 후보: 55개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.636006 | product_direct | 눈건강 루테인골드 | 케이지랩 주식회사 | products:8442/company_name@0:9 |
| 2 | 0.586556 | product_direct | 눈건강 루테인골드 | 20251014 | products:8442/registration_date@0:8 |
| 3 | 0.583657 | product_direct | 눈건강 루테인골드 | (다) 골다공증발생 위험 감소에 도움을 줌 | products:8442/main_functionality@312:335 |
| 4 | 0.578603 | product_direct | 눈건강 루테인골드 | 1. 성상 :  고유의 향미가 있고 이미, 이취가 없는 진한 주황색의 내용물을 포함한 갈흑색의 타원형 연질캡슐 | products:8442/specification@0:61 |
| 5 | 0.562467 | product_direct | 눈건강 루테인골드 | 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음 | products:8442/main_functionality@12:57 |

## db_047_gnvNr4R4Brc / c04

- 영상: https://www.youtube.com/watch?v=gnvNr4R4Brc
- 제품명: 눈건강 루테인 골드
- 제품 식별: matched
- Claim: **마리골드꽃추출물, 베타카로틴 비타민E, 아연, 셀렌**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=8442
- 전체 후보: 55개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.999235 | product_direct | 눈건강 루테인골드 | 7. 셀렌 : 표시량(16.5μg/500mg)의 80~150% | products:8442/specification@283:317 |
| 2 | 0.998847 | product_direct | 눈건강 루테인골드 | 3. 아연 : 표시량(7.2mg/500mg)의 80~150% | products:8442/specification@96:129 |
| 3 | 0.998757 | product_direct | 눈건강 루테인골드 | 4. 비타민E : 표시량(3.3mg α-TE/500mg)의 80~150% | products:8442/specification@130:170 |
| 4 | 0.998461 | product_direct | 눈건강 루테인골드 | (나) 피부와 점막을 형성하고 기능을 유지하는데 필요 | products:8442/main_functionality@132:161 |
| 5 | 0.998433 | product_direct | 눈건강 루테인골드 | 5. 비타민A : 표시량(700μg RAE/500mg)의 80~150% | products:8442/specification@171:210 |

## db_048_qdPDY6T86PU / c04

- 영상: https://www.youtube.com/watch?v=qdPDY6T86PU
- 제품명: 더 파인 프리미엄
- 제품 식별: matched
- Claim: **건강 기능 식품인데요**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=11123
- 전체 후보: 36개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.179291 | product_direct | 더파인프리미엄 | 건강한 혈당의 유지에 도움을 줄 수 있음. | products:11123/main_functionality@0:23 |
| 2 | 0.0799884 | product_direct | 더파인프리미엄 | 코스맥스바이오(주) | products:11123/company_name@0:10 |
| 3 | 0.0625631 | product_direct | 더파인프리미엄 | 고유의 향미가 있고 이미, 이취가 없는 연한 노랑색의 내용물을 함유한 투명한 타원형 연질캡슐 | products:11123/appearance@0:51 |
| 4 | 0.0426519 | product_direct | 더파인프리미엄 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 연한 노랑색의 내용물을 함유한 투명한 타원형 연질캡슐 | products:11123/specification@0:59 |
| 5 | 0.0397103 | product_direct | 더파인프리미엄 | 8) 총수은(mg/kg) : 0.5 이하 | products:11123/specification@238:260 |

## db_049_P-YTAviQgIM / c08

- 영상: https://www.youtube.com/watch?v=P-YTAviQgIM
- 제품명: 데이팩 올인원
- 제품 식별: matched
- Claim: **21종 멀티 비타민 & 미네랄**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=11268
- 전체 후보: 173개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.765382 | product_direct | 데이팩 올인원 | 21) 크롬 : 표시량 (15 µg / 1,640 mg)의 80~180% | products:11268/specification@885:925 |
| 2 | 0.558509 | product_direct | 데이팩 올인원 | 1일 1회, 1회 1팩(정제1, 경질캡슐1, 연질캡슐2)을 물과 함께 섭취하십시오. | products:11268/intake_method@0:46 |
| 3 | 0.55811 | product_direct | 데이팩 올인원 | 6) 비타민 B12 : 표시량 (24 µg / 1,640 mg)의 80~180% | products:11268/specification@243:287 |
| 4 | 0.528396 | product_direct | 데이팩 올인원 | - 비타민A : 어두운 곳에서 시각 적응을 위해 필요, 피부와 점막을 형성하고 기능을 유지하는데 필요, 상피세포의 성장과 발달에 필요 | products:11268/main_functionality@161:235 |
| 5 | 0.493762 | product_direct | 데이팩 올인원 | 4) 비타민 B2 : 표시량 (14 mg / 1,640 mg)의 80~180% | products:11268/specification@155:198 |

## db_053_t6SkBUwkzZ8 / c02

- 영상: https://www.youtube.com/watch?v=t6SkBUwkzZ8
- 제품명: 듀오락 위장간 케어
- 제품 식별: matched
- Claim: **감초추출물이 위!**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=12004
- 전체 후보: 33개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.940211 | product_direct | 듀오락 위장간 케어 | (영문) May help to stomach health by protecting gastric mucosa and inhibiting proliferation of Helicobacter pylori in gastric mucosa. | products:12004/main_functionality@181:312 |
| 2 | 0.923789 | product_direct | 듀오락 위장간 케어 | 1일 2회, 1회 2캡슐(0.8g)을 물과 함께 섭취하십시오. | products:12004/intake_method@0:34 |
| 3 | 0.916492 | product_direct | 듀오락 위장간 케어 | 5) 비타민 C: 표시량 (100mg/1.6g)의 80~150% | products:12004/specification@179:214 |
| 4 | 0.914262 | product_direct | 듀오락 위장간 케어 | 3) 글라브리딘: 표시량 (5.4mg/1.6g) 의 80~120% | products:12004/specification@107:143 |
| 5 | 0.908313 | product_direct | 듀오락 위장간 케어 | 설사, 위통, 복부팽만 등의 위장관계 장애가 나타나는 경우에는 섭취에 주의 | products:12004/intake_precautions@263:304 |

## db_055_UPPksFnfOcU / c10

- 영상: https://www.youtube.com/watch?v=UPPksFnfOcU
- 제품명: 드시모네 4500
- 제품 식별: matched
- Claim: **1회 분량 : 1포 (4.4 g)**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=12084
- 전체 후보: 28개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.697445 | product_direct | 드시모네 4500 | 성인의 경우 1일 1회 1포를 물과 함께 섭취하십시오. | products:12084/intake_method@0:30 |
| 2 | 0.500464 | product_direct | 드시모네 4500 | 3. 프로바이오틱스 수 : 표시량 450,000,000,000 CFU/4,400 mg)이상 | products:12084/specification@70:120 |
| 3 | 0.34232 | product_direct | 드시모네 4500 | [프로바이오틱스(드시모네)(제2009-28호)] | products:12084/main_functionality@0:26 |
| 4 | 0.289966 | product_direct | 드시모네 4500 | 1. 질환이 있거나 의약품 복용 시 전문가와 상담하십시오. | products:12084/intake_precautions@0:32 |
| 5 | 0.270841 | product_direct | 드시모네 4500 | 200700170351868 | products:12084/manufacturing_report_number@0:15 |

## db_061_5ED9Yi0UfBI / c05

- 영상: https://www.youtube.com/watch?v=5ED9Yi0UfBI
- 제품명: 루테인 지아잔틴 164
- 제품 식별: matched
- Claim: **Lutein  /  Zeaxanthin  /  Vitamin A**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=14188
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.988098 | product_direct | 루테인지아잔틴 164 | 4. 비타민A : 표시량(210ug RAE/500mg)의 80~150% | products:14188/specification@133:172 |
| 2 | 0.978345 | product_direct | 루테인지아잔틴 164 | 5. 비타민E : 표시량(3.3mg α-TE/500mg)의 80~150% | products:14188/specification@173:213 |
| 3 | 0.978236 | ingredient_reference | 루테인 지아잔틴 복합 추출물 | 루테인과 지아잔틴의 합으로서 10~20 mg | evidence:447 |
| 4 | 0.976473 | ingredient_reference | 루테인지아잔틴복합추출물 | 루테인과 지아잔틴의 합으로서 10~20 mg/일 | evidence:1310 |
| 5 | 0.97588 | product_direct | 루테인지아잔틴 164 | 고유의 향미가 있고 이미·이취가 없는 주황색의 점도가 있는 내용물을 함유한 흑갈색의 타원형 연질캡슐 | products:14188/appearance@0:55 |

## db_062_qmesmHU6NEM / c07

- 영상: https://www.youtube.com/watch?v=qmesmHU6NEM
- 제품명: 루테인 지아잔틴 164
- 제품 식별: matched
- Claim: **판매원 (주)뉴트리원**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=14188
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.485534 | product_direct | 루테인지아잔틴 164 | 1. 성상 : 고유의 향미가 있고 이미·이취가 없는 주황색의 점도가 있는 내용물을 함유한 흑갈색의 타원형 연질캡슐 | products:14188/specification@0:63 |
| 2 | 0.36978 | product_direct | 루테인지아잔틴 164 | 3. 총지아잔틴 : 표시량(4mg/500mg)의 80~120% | products:14188/specification@98:132 |
| 3 | 0.362888 | product_direct | 루테인지아잔틴 164 | 특정질환, 특이체질, 알레르기체질, 임산부의 경우에는 간혹 개인에 따라 과민반응이 나타날 수 있으므로 원료를 확인하시고, 섭취전에 전문가와 상담하시기 바랍니다. | products:14188/intake_precautions@85:174 |
| 4 | 0.347453 | product_direct | 루테인지아잔틴 164 | 고유의 향미가 있고 이미·이취가 없는 주황색의 점도가 있는 내용물을 함유한 흑갈색의 타원형 연질캡슐 | products:14188/appearance@0:55 |
| 5 | 0.339138 | product_direct | 루테인지아잔틴 164 | 8. 비타민B1 : 표시량(0.36mg/500mg)의 80~180% | products:14188/specification@284:321 |

## db_065_d1vRPXhgJAY / c11

- 영상: https://www.youtube.com/watch?v=d1vRPXhgJAY
- 제품명: 트리플 엑스 127
- 제품 식별: unmatched
- Claim: **건강기능식품**
- 식별 경로/사유: exact_name / multiple_candidates; product_id=None
- 전체 후보: 82개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.00896717 | ingredient_reference | EPA 및 DHA 함유 유지 | - | evidence:1004 |
| 2 | 0.00896717 | ingredient_reference | EPA 및 DHA 함유 유지 | - | evidence:1010 |
| 3 | 0.00896717 | ingredient_reference | EPA 및 DHA 함유 유지 | - | evidence:1650 |
| 4 | 0.00896717 | ingredient_reference | EPA 및 DHA 함유 유지 | - | evidence:202 |
| 5 | 0.00896717 | ingredient_reference | EPA 및 DHA 함유 유지 | - | evidence:434 |

## db_066_Qk_qjEMCsY8 / c05

- 영상: https://www.youtube.com/watch?v=Qk_qjEMCsY8
- 제품명: 루테인 지아잔틴 164
- 제품 식별: matched
- Claim: **루테인지아잔틴복합추출물+비타민4종+미네랄2종**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=14188
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.994629 | product_direct | 루테인지아잔틴 164 | ①정상적인 면역기능에 필요②정상적인 세포분열에 필요 | products:14188/main_functionality@104:132 |
| 2 | 0.993815 | product_direct | 루테인지아잔틴 164 | ①어두운 곳에서 시각 적응을 위해 필요②피부와 점막을 형성하고 기능을 유지하는데 필요③상피세포의 성장과 발달에 필요 | products:14188/main_functionality@133:197 |
| 3 | 0.993199 | product_direct | 루테인지아잔틴 164 | ①유해산소로부터 세포를 보호하는데 필요 | products:14188/main_functionality@82:103 |
| 4 | 0.992599 | product_direct | 루테인지아잔틴 164 | ①항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요 | products:14188/main_functionality@49:81 |
| 5 | 0.992589 | product_direct | 루테인지아잔틴 164 | 4. 비타민A : 표시량(210ug RAE/500mg)의 80~150% | products:14188/specification@133:172 |

## db_067_mAyGdVi1ErI / c09

- 영상: https://www.youtube.com/watch?v=mAyGdVi1ErI
- 제품명: 루테인 지아잔틴 164
- 제품 식별: matched
- Claim: **500 mg X 30캡슐 (15 g)**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=14188
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.627152 | product_direct | 루테인지아잔틴 164 | 2. 루테인 : 표시량(16mg/500mg)의 80~120% | products:14188/specification@64:97 |
| 2 | 0.594072 | product_direct | 루테인지아잔틴 164 | 4. 비타민A : 표시량(210ug RAE/500mg)의 80~150% | products:14188/specification@133:172 |
| 3 | 0.592949 | product_direct | 루테인지아잔틴 164 | 3. 총지아잔틴 : 표시량(4mg/500mg)의 80~120% | products:14188/specification@98:132 |
| 4 | 0.587178 | product_direct | 루테인지아잔틴 164 | 6. 아연 : 표시량(2.55mg/500mg)의 80~150% | products:14188/specification@214:248 |
| 5 | 0.579574 | product_direct | 루테인지아잔틴 164 | 7. 셀렌 : 표시량(16.5μg/500mg)의 80~150% | products:14188/specification@249:283 |

## db_074_tHG5O5CMHSA / c07

- 영상: https://www.youtube.com/watch?v=tHG5O5CMHSA
- 제품명: 리턴큐
- 제품 식별: unmatched
- Claim: **145 95 120 80 0주 1주 2주 3주 4주**
- 식별 경로/사유: exact_name / multiple_candidates; product_id=None
- 전체 후보: 3개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.160539 | ingredient_reference | 정어리펩타이드 SP100N(기능성원료인정제2004-1호) | (1) 고혈압치료제 등 복용 시 전문가와 상담할 것 (2) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 | evidence:1792 |
| 2 | 0.159065 | ingredient_reference | 정어리펩타이드 SP100N(기능성원료인정제2004-1호) | (국문) 혈압을 조절하는데 도움을 줄 수 있음 (영문) May help to maintain healthy blood pressure | evidence:1790 |
| 3 | 0.0982715 | ingredient_reference | 정어리펩타이드 SP100N(기능성원료인정제2004-1호) | 250 (μg) 400 (μg) | evidence:1791 |

## db_077_OP3AH0OqWjs / c04

- 영상: https://www.youtube.com/watch?v=OP3AH0OqWjs
- 제품명: 정어리 리턴큐
- 제품 식별: unmatched
- Claim: **남태평양 심해와 알래스카 청정해역에서 잡아서 더욱 믿을 수 있습니다.**
- 식별 경로/사유: full_name_damerau_levenshtein / manufacturer_missing_for_typo_route; product_id=None

**연결 가능한 Evidence 없음**

## db_078_mhzAWG1-UGw / c03

- 영상: https://www.youtube.com/watch?v=mhzAWG1-UGw
- 제품명: 마이니 딥슬립 이뮨
- 제품 식별: unmatched
- Claim: **락티움 테아닌 액상마그네슘 아연 판토텐산 비타민B6**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None
- 전체 후보: 25개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.981248 | ingredient_reference | 유단백가수분해물(락티움)(기능성원료인정제2020-2호) | 300 (mg) 300 (mg) | evidence:2475 |
| 2 | 0.971497 | ingredient_reference | 테아닌 | L-테아닌 으로서 200~250mg/일 | evidence:456 |
| 3 | 0.962042 | ingredient_reference | 유단백가수분해물(락티움)(기능성원료인정제2020-2호) | (1) 임산부, 수유여성 및 어린이는 섭취에 주의 (2) 우유 및 유제품에 대하여 알레르기를 나타내는 사람은 섭취에 주의 | evidence:2476 |
| 4 | 0.957516 | ingredient_reference | 테아닌(Theanine) | “스트레스로 인한 긴장을 완화시키는데 도움을 줄 수 있음” (기타기능 II) | evidence:426 |
| 5 | 0.95695 | ingredient_reference | 테아닌(Theanine) | L-테아닌 으로서 200~250 mg/일 | evidence:427 |

## db_079_WCQtPkMGCYE / c09

- 영상: https://www.youtube.com/watch?v=WCQtPkMGCYE
- 제품명: 마이니 딥슬립 이뮨
- 제품 식별: unmatched
- Claim: **액상 140ml + 정제 7g[액상 20ml + 정제 1g(정제1 500mg + 정제2 500mg)] × 7병**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None
- 전체 후보: 25개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.00116123 | ingredient_reference | 유단백가수분해물(락티움) | - 임산부, 수유여성 및 12세 이하 어린이는 섭취에 주의하여야 합니다.  - 우유 및 유제품에 대하여 알레르기를 나타내는 사람은 섭취에 주의하여야 합니다. | evidence:231 |
| 2 | 0.00111991 | ingredient_reference | 유단백가수분해물(락티움) | 1) 임산부, 수유여성 및 어린이는 섭취에 주의 2) 우유 및 유제품에 대하여 알레르기를 나타내는 사람은 섭취에 주의 | evidence:1465 |
| 3 | 0.00111991 | ingredient_reference | 유단백가수분해물(락티움) | 1) 임산부, 수유여성 및 어린이는 섭취에 주의 2) 우유 및 유제품에 대하여 알레르기를 나타내는 사람은 섭취에 주의 | evidence:579 |
| 4 | 0.00111645 | ingredient_reference | 유단백가수분해물(락티움) | 1) 임산부, 수유여성 및 12세 이하 어린이는 섭취에 주의하여야 합니다. 2) 우유 및 유제품에 대하여 알레르기를 나타내는 사람은 섭취에 주의하여야 합니다. | evidence:1131 |
| 5 | 0.00103754 | ingredient_reference | 유단백가수분해물(락티움) | 스트레스로 인한 긴장 완화에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:1463 |

## db_080_yPMKj9wxiKc / c04

- 영상: https://www.youtube.com/watch?v=yPMKj9wxiKc
- 제품명: 마이니 부스터 비타민
- 제품 식별: unmatched
- Claim: **올리브영 랭킹 전체 1위* *2024.03.08 올리브영 온라인몰 전체 랭킹 판매랭킹 기준**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_081_fN51LUYpxFE / c04

- 영상: https://www.youtube.com/watch?v=fN51LUYpxFE
- 제품명: 마이니 부스터 비타민
- 제품 식별: unmatched
- Claim: **제조원: (주)네추럴웨이**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_082_AnT61olLCjY / c07

- 영상: https://www.youtube.com/watch?v=AnT61olLCjY
- 제품명: 머슬파워
- 제품 식별: matched
- Claim: **강호동의 건강관리 비결 머슬파워로 여러분들도 오래오래 건강하세요~**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=16234
- 전체 후보: 43개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.619431 | product_direct | 머슬파워 | 3) 비타민B6 : 단백질 및 아미노산 이용에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요. | products:16234/main_functionality@56:115 |
| 2 | 0.550024 | product_direct | 머슬파워 | 1일 1회, 1회 1포(20g)를 씹어서 섭취하십시오. | products:16234/intake_method@0:30 |
| 3 | 0.511227 | product_direct | 머슬파워 | 4) 비타민B6 : 표시량(1.5mg/20g)의 80~150% | products:16234/specification@114:148 |
| 4 | 0.500591 | product_direct | 머슬파워 | 식사조절, 운동을 병행하는 것이 바람직합니다. | products:16234/intake_precautions@273:298 |
| 5 | 0.488794 | product_direct | 머슬파워 | 3) 비타민B2 : 표시량(1.4mg/20g)의 80~180% | products:16234/specification@79:113 |

## db_085_53dM_1gHF_Y / c04

- 영상: https://www.youtube.com/watch?v=53dM_1gHF_Y
- 제품명: 머슬파워
- 제품 식별: matched
- Claim: **국내최초 식약처 근력개선 기능성 인정 오미자추출물 쉬잔드린 함유**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=16234
- 전체 후보: 43개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.919537 | product_direct | 머슬파워 | 1) 오미자추출물 : 근력 개선에 도움을 줄 수 있음 | products:16234/main_functionality@0:29 |
| 2 | 0.850836 | ingredient_reference | 오미자추출물 | 근력 개선에 도움을 줄 수 있음, 관절 및 연골 건강에 도움을 줄 수 있음 | evidence:942 |
| 3 | 0.811723 | ingredient_reference | 오미자추출물(기능성원료인정제2018-9호) | (국문) 근력 개선에 도움을 줄 수 있음 (영문) Help to improve muscle strength | evidence:2370 |
| 4 | 0.792956 | product_direct | 머슬파워 | 2) 쉬잔드린 : 표시량(4.99912mg/20g)의 80~120% | products:16234/specification@41:78 |
| 5 | 0.618103 | ingredient_reference | 오미자추출물(기능성원료인정제2016-21호) | 783 (mg) 783 (mg) | evidence:2325 |

## db_086_UvRGjZ0WJTc / c15

- 영상: https://www.youtube.com/watch?v=UvRGjZ0WJTc
- 제품명: 메가셀렌
- 제품 식별: matched
- Claim: **16.8 g (280 mg x 60정)**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=16830
- 전체 후보: 14개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.23289 | product_direct | 메가셀렌 | 에스케이내추럴팜(주) | products:16830/company_name@0:11 |
| 2 | 0.157673 | product_direct | 메가셀렌 | 20040017106110 | products:16830/manufacturing_report_number@0:14 |
| 3 | 0.136254 | product_direct | 메가셀렌 | 20150522 | products:16830/registration_date@0:8 |
| 4 | 0.0920553 | product_direct | 메가셀렌 | 2. 셀레늄(셀렌) : 표시량(200ug / 1000mg)의 80%~150% | products:16830/specification@20:62 |
| 5 | 0.0784231 | product_direct | 메가셀렌 | 2) 과량 섭취시 부작용이 있을 수 있으며, 특정원료에 알레르기가 있거나, 질병치료나 약물투여 중인 분들은 섭취전 전문가와 상의하십시오. | products:16830/intake_precautions@24:100 |

## db_090_2D8qJ6NROCs / c29

- 영상: https://www.youtube.com/watch?v=2D8qJ6NROCs
- 제품명: 메타그린
- 제품 식별: unmatched
- Claim: **건강기능식품 광고**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_099_dSjddyyEbrQ / c05

- 영상: https://www.youtube.com/watch?v=dSjddyyEbrQ
- 제품명: 변할지도
- 제품 식별: matched
- Claim: **5 g × 30포 (150 g)**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=19499
- 전체 후보: 13개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.255716 | product_direct | 변할지도 | 1일 2회, 1회 1포(5.5g)씩 충분한 물과 함께 섭취 | products:19499/intake_method@0:32 |
| 2 | 0.253278 | product_direct | 변할지도 | 경성제약주식회사 | products:19499/company_name@0:8 |
| 3 | 0.152312 | product_direct | 변할지도 | 2004001507388 | products:19499/manufacturing_report_number@0:13 |
| 4 | 0.145318 | product_direct | 변할지도 | 1) 성상: 갈색의 환으로서 고유의 색택과 향미를 가지며 이미, 이취 없음 | products:19499/specification@0:41 |
| 5 | 0.119134 | product_direct | 변할지도 | 2) 식이섬유: 6.5g/11g(1일 섭취량)의 80%이상 | products:19499/specification@42:74 |

## db_100_X6OK887LWyA / c08

- 영상: https://www.youtube.com/watch?v=X6OK887LWyA
- 제품명: 보스웰리아 BCC
- 제품 식별: matched
- Claim: **7일 21일 37일 67일 97일**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=19634
- 전체 후보: 58개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.13018 | product_direct | 보스웰리아 BCC | (주)서흥 | products:19634/company_name@0:5 |
| 2 | 0.0894056 | product_direct | 보스웰리아 BCC | (1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 검은 갈색 또는 어두운 갈회색의 장방형 제피정제 | products:19634/specification@0:57 |
| 3 | 0.0843515 | product_direct | 보스웰리아 BCC | 고유의 향미가 있고 이미, 이취가 없는 검은 갈색 또는 어두운 갈회색의 장방형 제피정제 | products:19634/appearance@0:48 |
| 4 | 0.0649398 | product_direct | 보스웰리아 BCC | 보스웰리아추출물등복합물(Flexir) : (국문) 관절 및 연골 건강에 도움을 줄 수 있음 (영문) May help to maintain healthy joint and cartilage | products:19634/main_functionality@0:104 |
| 5 | 0.0641918 | product_direct | 보스웰리아 BCC | (1) 습기가 적고 직사광선을 받지 않는 서늘한 곳에 보관 하십시오. (2)  영ㆍ유아 및 어린이의 손이 닿지 않는 곳에 보관 하십시오. (3) 제품 개봉 후에는 흡습이 일어날 수 있으니 바로 섭취하십시오. | products:19634/storage_and_distribution_standard@0:115 |

## db_101_k9HPaTy2jAc / c06

- 영상: https://www.youtube.com/watch?v=k9HPaTy2jAc
- 제품명: 혈당케어 바나바잎
- 제품 식별: unmatched
- Claim: **GMP**
- 식별 경로/사유: whole_phrase_and_manufacturer / manufacturer_missing; product_id=None

**연결 가능한 Evidence 없음**

## db_102_j2gn9xONdJE / c15

- 영상: https://www.youtube.com/watch?v=j2gn9xONdJE
- 제품명: 비에날씬
- 제품 식별: unmatched
- Claim: **Lactobacillus gasseri BNR17**
- 식별 경로/사유: whole_phrase_and_manufacturer / manufacturer_missing; product_id=None
- 전체 후보: 9개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.803888 | ingredient_reference | Lactobacillus gasseri BNR17 | 체지방 감소에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:813 |
| 2 | 0.785743 | ingredient_reference | Lactobacillus gasseri BNR17(기능성원료인정제2017-6호) | (국문) 체지방 감소에 도움을 줄 수 있음(생리활성기능) (영문) May help to reduce body fat | evidence:2332 |
| 3 | 0.698937 | ingredient_reference | Lactobacillus gasseri BNR17(기능성원료인정제2014-5호) | (국문) 체지방 감소에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:2260 |
| 4 | 0.463904 | ingredient_reference | Lactobacillus gasseri BNR17 | Lactobacillus gasseri BNR17 로서 1×10^10 CFU/일 | evidence:814 |
| 5 | 0.433524 | ingredient_reference | Lactobacillus gasseri BNR17(기능성원료인정제2017-6호) | (1) 산성도가 낮은 음료나 뜨거운 물과 함께 복용하는 것을 피하는 것이 좋음 | evidence:2334 |

## db_103_B1QC0IfbbBg / c17

- 영상: https://www.youtube.com/watch?v=B1QC0IfbbBg
- 제품명: 뼈엔 엠비피 MBP
- 제품 식별: matched
- Claim: **GMP**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=21990
- 전체 후보: 28개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.480689 | product_direct | 뼈엔 엠비피MBP | ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌 | products:21990/main_functionality@62:117 |
| 2 | 0.365729 | product_direct | 뼈엔 엠비피MBP | (영문) May help to maintain healthy bone | products:21990/main_functionality@22:60 |
| 3 | 0.339031 | product_direct | 뼈엔 엠비피MBP | 6. 총수은(mg/kg) : 0.1 이하 | products:21990/specification@132:154 |
| 4 | 0.336123 | product_direct | 뼈엔 엠비피MBP | 1. 성상 : 이미, 이취가 없으며 고유의 향미가 있는 황회색의 분말을 함유한 백색 경질캡슐 | products:21990/specification@0:51 |
| 5 | 0.309973 | product_direct | 뼈엔 엠비피MBP | 5. 카드뮴(mg/kg) : 0.5 이하 | products:21990/specification@109:131 |

## db_105_ZvdLzOq3RmI / c21

- 영상: https://www.youtube.com/watch?v=ZvdLzOq3RmI
- 제품명: 센트룸 맨 더블업
- 제품 식별: matched
- Claim: **한국건강기능식품협회에서 광고심의 받은 광고물입니다.**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=22954
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.737901 | product_direct | 센트룸 맨 더블업 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 탁한 노란 분홍색의 장타원형 제피정제 | products:22954/specification@0:50 |
| 2 | 0.729695 | product_direct | 센트룸 맨 더블업 | - 비타민 D :  칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌 | products:22954/main_functionality@287:354 |
| 3 | 0.707367 | product_direct | 센트룸 맨 더블업 | 고유의 향미가 있고 이미, 이취가 없는 탁한 노란 분홍색의 장타원형 제피정제 | products:22954/appearance@0:42 |
| 4 | 0.704502 | product_direct | 센트룸 맨 더블업 | 5) 비타민B6 : 표시량(9.8 mg/1,380 mg)의 80~150% | products:22954/specification@177:217 |
| 5 | 0.698974 | product_direct | 센트룸 맨 더블업 | - 칼슘 : 뼈와 치아 형성에 필요, 신경과 근육 기능 유지에 필요, 정상적인 혈액응고에 필요, 골다공증발생 위험 감소에 도움을 줌 | products:22954/main_functionality@599:672 |

## db_107_vGLl-CPSrKY / c29

- 영상: https://www.youtube.com/watch?v=vGLl-CPSrKY
- 제품명: 제품 참조 미확인
- 제품 식별: unresolved_product_ref
- Claim: **항산화**

**연결 가능한 Evidence 없음**

## db_110_1iCNGuRKt2w / c09

- 영상: https://www.youtube.com/watch?v=1iCNGuRKt2w
- 제품명: 제품 참조 미확인
- 제품 식별: unresolved_product_ref
- Claim: ***2024 니콜라스홀 Global CHC database, DB6 멀티비타민 기준**

**연결 가능한 Evidence 없음**

## db_111_LVYFleyCAk4 / c02

- 영상: https://www.youtube.com/watch?v=LVYFleyCAk4
- 제품명: 센트룸 실버 우먼
- 제품 식별: matched
- Claim: **세계판매 1위 멀티비타민 브랜드**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=22960
- 전체 후보: 62개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.576245 | product_direct | 센트룸 실버 우먼 | - 비타민 D :  칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌 | products:22960/main_functionality@287:354 |
| 2 | 0.389033 | product_direct | 센트룸 실버 우먼 | 6) 비타민 B12 : 표시량(35 ug/1,534 mg)의 80~180% | products:22960/specification@225:266 |
| 3 | 0.385883 | product_direct | 센트룸 실버 우먼 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 연한 자줏빛 분홍색의 장타원형 제피정제 | products:22960/specification@0:51 |
| 4 | 0.354369 | product_direct | 센트룸 실버 우먼 | - 비타민 B6 : 단백질 및 아미노산 이용에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요 | products:22960/main_functionality@129:187 |
| 5 | 0.347487 | product_direct | 센트룸 실버 우먼 | 8) 비타민 D : 표시량(12.5 ug/1,534 mg)의 80~180% | products:22960/specification@308:349 |

## db_112_o3J1gXJxpa8 / c11

- 영상: https://www.youtube.com/watch?v=o3J1gXJxpa8
- 제품명: 센트룸 실버 우먼
- 제품 식별: matched
- Claim: **2508-PM-KR-CNT-25-00144**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=22960
- 전체 후보: 62개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.511703 | product_direct | 센트룸 실버 우먼 | 고유의 향미가 있고 이미, 이취가 없는 연한 자줏빛 분홍색의 장타원형 제피정제 | products:22960/appearance@0:43 |
| 2 | 0.425069 | product_direct | 센트룸 실버 우먼 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 연한 자줏빛 분홍색의 장타원형 제피정제 | products:22960/specification@0:51 |
| 3 | 0.373353 | product_direct | 센트룸 실버 우먼 | - 비타민 D :  칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌 | products:22960/main_functionality@287:354 |
| 4 | 0.314489 | product_direct | 센트룸 실버 우먼 | - 칼슘 : 뼈와 치아 형성에 필요, 신경과 근육 기능 유지에 필요, 정상적인 혈액응고에 필요, 골다공증발생 위험 감소에 도움을 줌 | products:22960/main_functionality@599:672 |
| 5 | 0.283456 | product_direct | 센트룸 실버 우먼 | - 비타민 C : 결합조직 형성과 기능유지에 필요, 철의 흡수에 필요, 항산화 작용을 하여 유해산소로부터 세포를 보호하는데 필요 | products:22960/main_functionality@215:286 |

## db_114_g7TzMEZKjaU / c04

- 영상: https://www.youtube.com/watch?v=g7TzMEZKjaU
- 제품명: 센트룸 에너지 구미
- 제품 식별: matched
- Claim: **비타민 B1·B2·B6, 나이아신**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=22963
- 전체 후보: 18개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.934815 | product_direct | 센트룸 에너지 구미 | (5) 비타민B2 : 표시량(0.98 mg/4.5g)의 80%~180% | products:22963/specification@165:204 |
| 2 | 0.928445 | product_direct | 센트룸 에너지 구미 | (2) 나이아신 : 표시량(10.5 mg NE/4.5g)의 80%~150% | products:22963/specification@43:84 |
| 3 | 0.926865 | product_direct | 센트룸 에너지 구미 | 비타민B2 : 체내 에너지 생성에 필요 | products:22963/main_functionality@109:130 |
| 4 | 0.912004 | product_direct | 센트룸 에너지 구미 | 나이아신 : 체내 에너지 생성에 필요 | products:22963/main_functionality@0:20 |
| 5 | 0.904676 | product_direct | 센트룸 에너지 구미 | (3) 비타민B6 : 표시량(1.05 mg/4.5g)의 80%~150% | products:22963/specification@85:124 |

## db_116_m_w5BCSok00 / c08

- 영상: https://www.youtube.com/watch?v=m_w5BCSok00
- 제품명: 센트룸 타마플렉스 올인원 관절·연골·근육
- 제품 식별: matched
- Claim: **광고심의필  /  2504-PM-KR-CNT-25-00031**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=22980
- 전체 후보: 38개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.7462 | product_direct | 센트룸 타마플렉스 올인원 관절·연골·근육 | - 타마린드강황주정추출복합물(Tamaflex®)(제2024-12호) : 관절 및 연골 건강에 도움을 줄 수 있음 | products:22980/main_functionality@0:62 |
| 2 | 0.734995 | product_direct | 센트룸 타마플렉스 올인원 관절·연골·근육 | - 칼슘 : 뼈와 치아 형성에 필요, 신경과 근육 기능 유지에 필요, 정상적인 혈액응고에 필요, 골다공증발생 위험 감소에 도움을 줌 | products:22980/main_functionality@165:238 |
| 3 | 0.716685 | product_direct | 센트룸 타마플렉스 올인원 관절·연골·근육 | - 비타민 D : 칼슘과 인이 흡수되고 이용되는데 필요, 뼈의 형성과 유지에 필요, 골다공증발생 위험 감소에 도움을 줌 | products:22980/main_functionality@63:129 |
| 4 | 0.652278 | product_direct | 센트룸 타마플렉스 올인원 관절·연골·근육 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 탁한 노란 분홍색의 장타원형 제피정제 | products:22980/specification@0:50 |
| 5 | 0.596905 | product_direct | 센트룸 타마플렉스 올인원 관절·연골·근육 | 고유의 향미가 있고 이미, 이취가 없는 탁한 노란 분홍색의 장타원형 제피정제 | products:22980/appearance@0:42 |

## db_120_QUwiyY9Qh_k / c03

- 영상: https://www.youtube.com/watch?v=QUwiyY9Qh_k
- 제품명: 셀로맥스 가네요
- 제품 식별: matched
- Claim: **담즙 분비를 촉진해**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=23070
- 전체 후보: 25개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.926827 | ingredient_reference | 아티초크추출물 | “담즙분비를 촉진하여 지방 소화에 도움을 줄 수 있음(기타기능 II)” | evidence:361 |
| 2 | 0.919037 | ingredient_reference | 아티초크 추출물(기능성원료인정제2010-8호) | (국문) 담즙분비를 촉진하여 지방 소화에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:2043 |
| 3 | 0.903583 | product_direct | 셀로맥스 가네요 | - 담즙분비를 촉진하여 지방 소화에 도움을 줄 수 있음 | products:23070/main_functionality@0:30 |
| 4 | 0.449482 | ingredient_reference | 아티초크 추출물(기능성원료인정제2010-8호) | (1) 담관에 이상이 있는 분은 의사와 상의하신 후 섭취하시기 바랍니다. (2) 알레르기 반응이 나타나는 경우에는 섭취를 중단하시기 바랍니다. | evidence:2045 |
| 5 | 0.391789 | product_direct | 셀로맥스 가네요 | - May help fat digestion by facilitating the secretion of bile acid | products:23070/main_functionality@31:98 |

## db_121_p3YufTgQRHA / c12

- 영상: https://www.youtube.com/watch?v=p3YufTgQRHA
- 제품명: 셀로맥스 명품 알티지 오메가3
- 제품 식별: unmatched
- Claim: **AlaskOmega is a trademark of Wiley Companies**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None
- 전체 후보: 82개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.000850346 | ingredient_reference | EPA 및 DHA 함유 유지 | 「건강기능식품 기능성 원료 및 기준․규격  인정에 관한 규정」 제10조제2항에 따라 「건강기능식품의 기준 및 규격」에 고시 예정임 | evidence:97 |
| 2 | 0.000850346 | ingredient_reference | EPA 및 DHA 함유 유지 | 「건강기능식품 기능성 원료 및 기준․규격  인정에 관한 규정」 제10조제2항에 따라 「건강기능식품의 기준 및 규격」에 고시 예정임 | evidence:983 |
| 3 | 0.000770946 | ingredient_reference | EPA 및 DHA 함유유지 | 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:1132 |
| 4 | 0.000770946 | ingredient_reference | EPA 및 DHA 함유유지 | 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:158 |
| 5 | 0.000770946 | ingredient_reference | EPA 및 DHA 함유유지 | 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:647 |

## db_122_pKOtz25IIbs / c04

- 영상: https://www.youtube.com/watch?v=pKOtz25IIbs
- 제품명: 셀로맥스 명품 코랄 플러스
- 제품 식별: matched
- Claim: **칼슘, 마그네슘, 비타민D, 비타민K 제품**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=23106
- 전체 후보: 24개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.998832 | product_direct | 셀로맥스 명품 코랄플러스 | 5. 마그네슘 : 표시량(120mg/2400mg)의 80~150% | products:23106/specification@155:191 |
| 2 | 0.998739 | product_direct | 셀로맥스 명품 코랄플러스 | 2. 비타민 D : 표시량(25ug/2400mg)의 80~180% | products:23106/specification@46:82 |
| 3 | 0.998697 | product_direct | 셀로맥스 명품 코랄플러스 | 3. 비타민 K : 표시량(98ug/2400mg)의 80~180% | products:23106/specification@83:119 |
| 4 | 0.998636 | product_direct | 셀로맥스 명품 코랄플러스 | 4. 칼슘 : 표시량(485mg/2400mg)의 80~150% | products:23106/specification@120:154 |
| 5 | 0.998436 | product_direct | 셀로맥스 명품 코랄플러스 | [비타민D]①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌 | products:23106/main_functionality@138:199 |

## db_124_h7te3HAxv-A / c17

- 영상: https://www.youtube.com/watch?v=h7te3HAxv-A
- 제품명: 솔가 비오틴 5000
- 제품 식별: unmatched
- Claim: **건강기능식품 광고 입니다**
- 식별 경로/사유:  / conflicting_input_identity_observations; product_id=None

**연결 가능한 Evidence 없음**

## db_125_M4AD7_oBfp4 / c17

- 영상: https://www.youtube.com/watch?v=M4AD7_oBfp4
- 제품명: 어린이 수퍼바이오틱스
- 제품 식별: matched
- Claim: **건강기능식품**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27544
- 전체 후보: 18개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.58571 | product_direct | 어린이 수퍼바이오틱스 | 프로바이오틱스 : (1) 유산균 증식 및 유해균 억제에 도움을 줄 수 있음 (2) 배변활동 원활에 도움을 줄 수 있음 (3) 장 건강에 도움을 줄 수 있음 | products:27544/main_functionality@0:86 |
| 2 | 0.57409 | product_direct | 어린이 수퍼바이오틱스 | 1일 1회, 1회 1포(1g)를 직접 또는 물과 함께 섭취하십시오. | products:27544/intake_method@0:37 |
| 3 | 0.569025 | product_direct | 어린이 수퍼바이오틱스 | 20190604 | products:27544/registration_date@0:8 |
| 4 | 0.530388 | product_direct | 어린이 수퍼바이오틱스 | ① 성상 : 고유의 향미가 있고 이미, 이취가 없는 흰 분홍색의 분말 | products:27544/specification@0:38 |
| 5 | 0.529726 | product_direct | 어린이 수퍼바이오틱스 | ② 프로바이오틱스 수 : 표시량[5,000,000,000(50억)CFU/1.0g] 이상 | products:27544/specification@39:87 |

## db_126_1c3ZmUXrc8A / c05

- 영상: https://www.youtube.com/watch?v=1c3ZmUXrc8A
- 제품명: 수퍼바이오틱스 콜레스테롤
- 제품 식별: matched
- Claim: **Gut Health & Cholesterol Improvement**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=23601
- 전체 후보: 32개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.937969 | product_direct | 수퍼바이오틱스 콜레스테롤 | 유산균복합물(AB-LIFE) : (국문) 혈중 콜레스테롤 개선에 도움을 줄 수 있음, (영문) May help to reduce blood cholesterol levels,  유산균 증식 및 유해균 억제에 도움을 줄 수 있음, 배변활동 원활에 도움을 줄 수 있음, 장 건강에 도움을 줄 수 있음 | products:23601/main_functionality@0:165 |
| 2 | 0.820306 | product_direct | 수퍼바이오틱스 콜레스테롤 | 1일 1회, 1회 1캡슐(0.3g)을 충분한 물과 함께 섭취하십시오. | products:23601/intake_method@0:38 |
| 3 | 0.664213 | product_direct | 수퍼바이오틱스 콜레스테롤 | 20220530 | products:23601/registration_date@0:8 |
| 4 | 0.649581 | product_direct | 수퍼바이오틱스 콜레스테롤 | (주)서흥 | products:23601/company_name@0:5 |
| 5 | 0.642612 | product_direct | 수퍼바이오틱스 콜레스테롤 | (1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 노란 하양 또는 흰 노란색의 분말을 함유한 투명한 경질캡슐 | products:23601/specification@0:63 |

## db_127_kNWjguHhRs4 / c05

- 영상: https://www.youtube.com/watch?v=kNWjguHhRs4
- 제품명: 시그니처 파이토 이뮨
- 제품 식별: matched
- Claim: **2021~ 대한민국 국가대표 선수협회 MOU 체결**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=24705
- 전체 후보: 68개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.45891 | product_direct | 시그니처 파이토 이뮨 | 1)성상 : 고유의 색택과 향미를 가지며 이미·이취가 없는 진한 빨간색의 유상액을 함유한 적갈색 타원형의 연질캡슐 | products:24705/specification@375:438 |
| 2 | 0.44077 | product_direct | 시그니처 파이토 이뮨 | 1)성상 : 고유의 향미가 있고 이미, 이취가 없는 연한 노란색 장방형의 제피정제 | products:24705/specification@15:60 |
| 3 | 0.411414 | product_direct | 시그니처 파이토 이뮨 | 1)성상 : 고유의 색택과 향미를 가지며 이미·이취가 없는 연갈색의 액상 | products:24705/specification@814:854 |
| 4 | 0.290012 | product_direct | 시그니처 파이토 이뮨 | 고유의 향미가 있고 이미, 이취가 없는 연한 노란색 장방형의 제피정제 / 고유의 색택과 향미를 가지며 이미·이취가 없는 진한 빨간색의 유상액을 함유한 적갈색 타원형의 연질캡슐 / 고유의 색택과 향미를 가지며 이미·이취가 없는 연갈색의 액상 | products:24705/appearance@0:133 |
| 5 | 0.1984 | product_direct | 시그니처 파이토 이뮨 | ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌 | products:24705/main_functionality@184:239 |

## db_128_0nXNWl3B1Z4 / c03

- 영상: https://www.youtube.com/watch?v=0nXNWl3B1Z4
- 제품명: 시그니처 파이토 이뮨
- 제품 식별: unmatched
- Claim: **섭취방법 : 뚜껑을 개봉하여 정제+연질캡슐을 액상과 함께 섭취**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_131_J5Ofe99LM0U / c06

- 영상: https://www.youtube.com/watch?v=J5Ofe99LM0U
- 제품명: 시그니처 파이토 이뮨
- 제품 식별: unmatched
- Claim: **액상 200 ml + 정제 6g + 캡슐 5g**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_132__MNYBmy24nk / c02

- 영상: https://www.youtube.com/watch?v=_MNYBmy24nk
- 제품명: 아이메가 rTG 오메가3 미니
- 제품 식별: matched
- Claim: **미니캡슐**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=25915
- 전체 후보: 100개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.610243 | product_direct | 아이메가 rTG 오메가3 미니 | 1. 성상 : 고유의 향미가 있고 이미, 이취가 없는 연노랑의 내용물을 함유한 투명한 타원형 연질 캡슐 | products:25915/specification@0:57 |
| 2 | 0.578264 | product_direct | 아이메가 rTG 오메가3 미니 | 1일 1회, 1회 2캡슐을 물과 함께 섭취하십시오. | products:25915/intake_method@0:28 |
| 3 | 0.555004 | product_direct | 아이메가 rTG 오메가3 미니 | 고유의 향미가 있고 이미, 이취가 없는 연노랑의 내용물을 함유한 투명한 타원형 연질 캡슐 | products:25915/appearance@0:49 |
| 4 | 0.437175 | product_direct | 아이메가 rTG 오메가3 미니 | [EPA 및 DHA 함유 유지] 혈중 중성지질 개선･혈행 개선에 도움을 줄 수 있음 | products:25915/main_functionality@0:46 |
| 5 | 0.399016 | product_direct | 아이메가 rTG 오메가3 미니 | 3. EPA와 DHA의 합 : 표시량(500mg/668mg)의 80~120% | products:25915/specification@76:118 |

## db_134_eBXQtWMPUGM / c01

- 영상: https://www.youtube.com/watch?v=eBXQtWMPUGM
- 제품명: 아이세이프 루테인
- 제품 식별: unmatched
- Claim: **내 눈을 편안하게 아이세이프 루테인**
- 식별 경로/사유: full_name_damerau_levenshtein / manufacturer_missing_for_typo_route; product_id=None
- 전체 후보: 3개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.932706 | ingredient_reference | 루테인 | “노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줌”(기타기능Ⅰ) | evidence:423 |
| 2 | 0.814728 | ingredient_reference | 루테인 | 루테인으로서 10～20mg | evidence:424 |
| 3 | 0.520862 | ingredient_reference | 루테인 | 1) 과다 섭취 시 일시적으로 피부가 황색으로 변할 수 있음 | evidence:425 |

## db_135_0EkaCDWmB04 / c08

- 영상: https://www.youtube.com/watch?v=0EkaCDWmB04
- 제품명: 아이시안 루테인 지아잔틴 플러스케어
- 제품 식별: matched
- Claim: **건강기능식품**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=25970
- 전체 후보: 59개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.719924 | product_direct | 아이시안 루테인 지아잔틴 플러스 케어 | (1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 선명한 빨강 주황색의 점도가 있는 내용물을 함유한 흑갈색 타원형 연질캡슐 | products:25970/specification@0:71 |
| 2 | 0.710801 | product_direct | 아이시안 루테인 지아잔틴 플러스 케어 | 루테인지아잔틴복합추출물(제2018-4호) : (국문) (1) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음 (2) 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음, (영문) (1) May help the eye health by maintaining the density of macular pigments which can be decreased by … | products:25970/main_functionality@0:284 |
| 3 | 0.641077 | product_direct | 아이시안 루테인 지아잔틴 플러스 케어 | 고유의 향미가 있고 이미, 이취가 없는 선명한 빨강 주황색의 점도가 있는 내용물을 함유한 흑갈색 타원형 연질캡슐 | products:25970/appearance@0:62 |
| 4 | 0.617882 | product_direct | 아이시안 루테인 지아잔틴 플러스 케어 | 비타민B6 : (1) 단백질 및 아미노산 이용에 필요 (2) 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요 | products:25970/main_functionality@365:427 |
| 5 | 0.561394 | product_direct | 아이시안 루테인 지아잔틴 플러스 케어 | (6) 비타민B6 : 표시량(1.5 mg/0.3g)의 80%~150% | products:25970/specification@232:270 |

## db_136_40OyEPJBj1E / c12

- 영상: https://www.youtube.com/watch?v=40OyEPJBj1E
- 제품명: 아이원 루테인지아잔틴 미니
- 제품 식별: matched
- Claim: **4년 연속 구매율 1위* 안국건강**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=26056
- 전체 후보: 51개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.676203 | product_direct | 아이원 루테인지아잔틴 미니 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 진한 빨강색의 유상 내용물을 함유한 갈흑색의 타원형 연질캡슐 | products:26056/specification@0:63 |
| 2 | 0.582857 | product_direct | 아이원 루테인지아잔틴 미니 | 고유의 향미가 있고 이미, 이취가 없는 진한 빨강색의 유상 내용물을 함유한 갈흑색의 타원형 연질캡슐 | products:26056/appearance@0:55 |
| 3 | 0.410514 | product_direct | 아이원 루테인지아잔틴 미니 | 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음, 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음. | products:26056/main_functionality@0:76 |
| 4 | 0.353203 | product_direct | 아이원 루테인지아잔틴 미니 | 제조일로부터 3년 | products:26056/shelf_life@0:9 |
| 5 | 0.315584 | product_direct | 아이원 루테인지아잔틴 미니 | 1일 1회, 1회 1캡슐을 충분한 물과 함께 섭취하십시오. | products:26056/intake_method@0:32 |

## db_139_3ClBJSsUX04 / c05

- 영상: https://www.youtube.com/watch?v=3ClBJSsUX04
- 제품명: 아이커
- 제품 식별: matched
- Claim: **우리아이 성장기 올바른 키성장을 위한 선택**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=26086
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.791022 | product_direct | 아이커 | -키 성장에는 충분한 영양섭취, 적절한 수면, 건강한 생활습관·운동을 병행하여야 함. | products:26086/intake_precautions@181:228 |
| 2 | 0.775436 | product_direct | 아이커 | [황기추출물 등 복합물] (국문) 어린이 키성장에 도움을 줄 수 있음 (영문) May help to children grow taller | products:26086/main_functionality@0:76 |
| 3 | 0.348083 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (국문) 어린이 키성장에 도움을 줄 수 있음 (영문) May help to children grow taller | evidence:2234 |
| 4 | 0.319507 | product_direct | 아이커 | [비타민D]①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌 | products:26086/main_functionality@224:285 |
| 5 | 0.294813 | product_direct | 아이커 | 1일 1회, 1회 1포를 우유와 함께 섭취하십시오. | products:26086/intake_method@0:28 |

## db_141_F1owLR8fI-Y / c08

- 영상: https://www.youtube.com/watch?v=F1owLR8fI-Y
- 제품명: 아이커
- 제품 식별: matched
- Claim: **아연**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=26086
- 전체 후보: 64개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.387562 | product_direct | 아이커 | 17) 아연 : 표시량 (8mg/12g)의 80~150% | products:26086/specification@637:668 |
| 2 | 0.227646 | product_direct | 아이커 | [아연] ①정상적인 면역기능에 필요②정상적인 세포분열에 필요 | products:26086/main_functionality@462:495 |
| 3 | 0.0773607 | product_direct | 아이커 | -특정원료에 알레르기가 있거나 장기간 또는 의약품 복용시 전문가와 상담 후 섭취하십시오. | products:26086/intake_precautions@23:72 |
| 4 | 0.0760728 | product_direct | 아이커 | 종근당건강(주) | products:26086/company_name@0:8 |
| 5 | 0.0659772 | product_direct | 아이커 | 고유의 향미가 있고 이미, 이취가 없는 흰색, 회갈색, 흑갈색의 분말 | products:26086/appearance@0:38 |

## db_143_iPlIpMrGcp0 / c04

- 영상: https://www.youtube.com/watch?v=iPlIpMrGcp0
- 제품명: 아이클리어 루테인지아잔틴
- 제품 식별: matched
- Claim: **황반의 중심 물질 지아잔틴**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=26126
- 전체 후보: 63개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.657086 | ingredient_reference | 루테인지아잔틴복합추출물(제2019-16호) | (국문) ① 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음 ② 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음 (영문) ① May help the eye health by maintaining the density of macular pigments which can be decreased by aging ② May help to maintain eye… | evidence:2390 |
| 2 | 0.638149 | ingredient_reference | 루테인/지아잔틴 복합추출물(기능성원료인정제2008-66호) | (국문) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈건강에 도움을 줄 수 있음 (영문) May help the eye health by maintaining the density of macular pigments which can be decreased by aging | evidence:1879 |
| 3 | 0.585443 | ingredient_reference | 루테인지아잔틴복합추출물(기능성원료인정제2018-4호) | (국문) ① 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음 ② 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음 (영문) ① May help the eye health by maintaining the density of macular pigments which can be decreased by aging ② May help to maintain eye… | evidence:2358 |
| 4 | 0.526654 | ingredient_reference | 루테인지아잔틴복합추출물(기능성원료인정제2018-11호) | (국문) 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈건강에 도움을 줄 수 있음 (영문) May help the eye health by maintaining the density of macular pigments which can be decreased by aging | evidence:2338 |
| 5 | 0.397046 | ingredient_reference | 루테인지아잔틴복합추출물 | 노화로 인해 감소될 수 있는 황반색소밀도를 유지하여 눈 건강에 도움을 줄 수 있음 | evidence:1309 |

## db_147_68LD5c_NAQ8 / c11

- 영상: https://www.youtube.com/watch?v=68LD5c_NAQ8
- 제품명: 아이클타임
- 제품 식별: matched
- Claim: **시험기간 및 섭취량 : 12주, 황기 추출물 등 복합물 1.5g/day**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=26136
- 전체 후보: 41개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.810042 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (국문) 어린이 키성장에 도움을 줄 수 있음 (영문) May help to children grow taller | evidence:2234 |
| 2 | 0.79178 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (1) 임산부 및 수유부는 섭취를 피할 것 (2) 특정원료에 알레르기가 있거나 장기간 또는 의약품 복용시 전문가와 상담할 것 (3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 (4) 키 성장에는 충분한 영양섭취, 적절한 수면, 건강한 생활습관ㆍ운동을 병행하여야 함 | evidence:2236 |
| 3 | 0.722137 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | 2 (g/일) 2 (g/일) | evidence:2235 |
| 4 | 0.561717 | product_direct | 아이클타임 | 20230314 | products:26136/registration_date@0:8 |
| 5 | 0.499612 | product_direct | 아이클타임 | 특정질환, 특이체질, 알레르기체질, 임산부의 경우에는 간혹 개인에 따라 과민반응이 나타날 수 있으므로 원료를 확인하시고, 섭취전에 전문가와 상담하시기 바랍니다. | products:26136/intake_precautions@0:89 |

## db_149_oFkaj0c3LoE / c09

- 영상: https://www.youtube.com/watch?v=oFkaj0c3LoE
- 제품명: 아이클타임
- 제품 식별: matched
- Claim: **시험기관 : 국내 대학병원 (경희 대학교) RCT 인체적용 시험**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=26136
- 전체 후보: 41개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.22298 | product_direct | 아이클타임 | ①뼈와 치아 형성에 필요②신경과 근육 기능 유지에 필요③정상적인 혈액응고에 필요④골다공증발생 위험 감소에 도움을 줌 | products:26136/main_functionality@128:192 |
| 2 | 0.208526 | product_direct | 아이클타임 | 특정질환, 특이체질, 알레르기체질, 임산부의 경우에는 간혹 개인에 따라 과민반응이 나타날 수 있으므로 원료를 확인하시고, 섭취전에 전문가와 상담하시기 바랍니다. | products:26136/intake_precautions@0:89 |
| 3 | 0.191484 | product_direct | 아이클타임 | 면역력 증진･피로개선에 도움을 줄 수 있음 | products:26136/main_functionality@63:86 |
| 4 | 0.161693 | product_direct | 아이클타임 | 혈소판 응집억제를 통한 혈액흐름･기억력 개선･항산화에 도움을 줄 수 있음 | products:26136/main_functionality@87:127 |
| 5 | 0.156899 | product_direct | 아이클타임 | 1. 성상 : 고유의 향미가 있고 이미·이취가 없는 빨간검정색의 액상 | products:26136/specification@0:38 |

## db_150_2E-n2nFG6fU / c03

- 영상: https://www.youtube.com/watch?v=2E-n2nFG6fU
- 제품명: 아이클타임
- 제품 식별: matched
- Claim: **황기 추출물 등 복합물 (HT042) 국내 최초 키성장 기능성 · 안전성 인정**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=26136
- 전체 후보: 41개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.831621 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (국문) 어린이 키성장에 도움을 줄 수 있음 (영문) May help to children grow taller | evidence:2234 |
| 2 | 0.743671 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (1) 임산부 및 수유부는 섭취를 피할 것 (2) 특정원료에 알레르기가 있거나 장기간 또는 의약품 복용시 전문가와 상담할 것 (3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 (4) 키 성장에는 충분한 영양섭취, 적절한 수면, 건강한 생활습관ㆍ운동을 병행하여야 함 | evidence:2236 |
| 3 | 0.489458 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | 2 (g/일) 2 (g/일) | evidence:2235 |
| 4 | 0.414587 | product_direct | 아이클타임 | (국문) 어린이 키성장에 도움을 줄 수 있음 | products:26136/main_functionality@0:24 |
| 5 | 0.410475 | product_direct | 아이클타임 | (영문) May help to children grow taller | products:26136/main_functionality@25:62 |

## db_154_O0VmSF9Ks0U / c02

- 영상: https://www.youtube.com/watch?v=O0VmSF9Ks0U
- 제품명: 아이클타임
- 제품 식별: unmatched
- Claim: **대한민국 대표 키성장 아이클타임**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None
- 전체 후보: 8개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.439412 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (국문) 어린이 키성장에 도움을 줄 수 있음 (영문) May help to children grow taller | evidence:2234 |
| 2 | 0.389362 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (1) 임산부 및 수유부는 섭취를 피할 것 (2) 특정원료에 알레르기가 있거나 장기간 또는 의약품 복용시 전문가와 상담할 것 (3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 (4) 키 성장에는 충분한 영양섭취, 적절한 수면, 건강한 생활습관ㆍ운동을 병행하여야 함 | evidence:2236 |
| 3 | 0.0656043 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | 2 (g/일) 2 (g/일) | evidence:2235 |
| 4 | 0.0240232 | ingredient_reference | 홍삼 | 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 22~80mg | evidence:1558 |
| 5 | 0.0133806 | ingredient_reference | 홍삼(제2024-20호) | 23 (mg/일) 23 (mg/일) | evidence:2799 |

## db_156_DQi8J-8WkZ0 / c12

- 영상: https://www.youtube.com/watch?v=DQi8J-8WkZ0
- 제품명: 아이클타임
- 제품 식별: unmatched
- Claim: **판매원 (주)두드림**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None
- 전체 후보: 8개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.000337537 | ingredient_reference | 홍삼(제2024-20호) | (1) 당뇨치료제 및 혈액항응고제 복용 시 섭취에 주의 (2) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음 (3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 | evidence:2800 |
| 2 | 0.000218286 | ingredient_reference | 홍삼(제2024-20호) | (국문) 혈당조절에 도움을 줄 수 있음 (영문) May help to maintain healthy blood glucose levels | evidence:2798 |
| 3 | 0.000198185 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (1) 임산부 및 수유부는 섭취를 피할 것 (2) 특정원료에 알레르기가 있거나 장기간 또는 의약품 복용시 전문가와 상담할 것 (3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 (4) 키 성장에는 충분한 영양섭취, 적절한 수면, 건강한 생활습관ㆍ운동을 병행하여야 함 | evidence:2236 |
| 4 | 0.000179026 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | 2 (g/일) 2 (g/일) | evidence:2235 |
| 5 | 0.000178615 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (국문) 어린이 키성장에 도움을 줄 수 있음 (영문) May help to children grow taller | evidence:2234 |

## db_157_-kjoqO9Um6Q / c07

- 영상: https://www.youtube.com/watch?v=-kjoqO9Um6Q
- 제품명: 아이클타임
- 제품 식별: unmatched
- Claim: **국내최초! 키성장 기능성 · 안전성 인정**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None
- 전체 후보: 8개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.0401925 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (국문) 어린이 키성장에 도움을 줄 수 있음 (영문) May help to children grow taller | evidence:2234 |
| 2 | 0.0208838 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | (1) 임산부 및 수유부는 섭취를 피할 것 (2) 특정원료에 알레르기가 있거나 장기간 또는 의약품 복용시 전문가와 상담할 것 (3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 (4) 키 성장에는 충분한 영양섭취, 적절한 수면, 건강한 생활습관ㆍ운동을 병행하여야 함 | evidence:2236 |
| 3 | 0.000568163 | ingredient_reference | 황기추출물 등 복합물(HT042)(기능성원료인정제2014-40호) | 2 (g/일) 2 (g/일) | evidence:2235 |
| 4 | 0.000290649 | ingredient_reference | 홍삼 | 진세노사이드 Rg1, Rb1 및 Rg3의 합계로서 22~80mg | evidence:1558 |
| 5 | 0.00016237 | ingredient_reference | 홍삼(제2024-20호) | (1) 당뇨치료제 및 혈액항응고제 복용 시 섭취에 주의 (2) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음 (3) 이상사례 발생 시 섭취를 중단하고 전문가와 상담할 것 | evidence:2800 |

## db_160_qBFBNIBlB3Q / c34

- 영상: https://www.youtube.com/watch?v=qBFBNIBlB3Q
- 제품명: 프로바이오틱스 유산균 스페셜핏
- 제품 식별: unmatched
- Claim: **건강기능식품**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_164_Gl7-zKA-GwI / c22

- 영상: https://www.youtube.com/watch?v=Gl7-zKA-GwI
- 제품명: 애터미 알티지 오메가3
- 제품 식별: matched
- Claim: **우수건강기능식품제조기준 GMP**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27050
- 전체 후보: 103개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.538067 | product_direct | 애터미 알티지 오메가3 | 1) EPA 및 DHA 함유 유지: (가) 혈중 중성지질 개선•혈행 개선에 도움을 줄 수 있음 (나) 건조한 눈을 개선하여 눈 건강에 도움을 줄 수 있음 | products:27050/main_functionality@0:85 |
| 2 | 0.521759 | product_direct | 애터미 알티지 오메가3 | 1. 성상 : 고유의 향미가 있고 이미, 이취가 없으며 연한 노란색의 내용물을 함유한 연한 노란색의 장용성 타원형 연질캡슐 | products:27050/specification@0:68 |
| 3 | 0.428936 | product_direct | 애터미 알티지 오메가3 | - 연질캡슐 특성상 보관 상태에 따라 외형 및 성상 변화가 생기 우려가 있으니 반드시 고온다습한 곳과 직사광선을 피하여 건조한 실온에 보관하십시오- 어린이의 손에 닿지 않는곳에 보관하십시오 | products:27050/storage_and_distribution_standard@0:105 |
| 4 | 0.425087 | product_direct | 애터미 알티지 오메가3 | 5. 카드뮴(mg/kg) : 1.0 이하 | products:27050/specification@192:214 |
| 5 | 0.417141 | product_direct | 애터미 알티지 오메가3 | 고유의 향미가 있고 이미, 이취가 없으며 연한 노란색의 내용물을 함유한 연한 노란색의 장용성 타원형 연질캡슐 | products:27050/appearance@0:60 |

## db_166_eoe2GUtz4v8 / c08

- 영상: https://www.youtube.com/watch?v=eoe2GUtz4v8
- 제품명: 애터미 터마신 MSM
- 제품 식별: unmatched
- Claim: **752 mg x 128 정 (96.256 g)**
- 식별 경로/사유: exact_name / multiple_candidates; product_id=None
- 전체 후보: 24개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.0171333 | ingredient_reference | 강황 추출물(터마신)(기능성원료인정제2014-2호) | 1 (g) 1 (g) | evidence:2211 |
| 2 | 0.0157588 | ingredient_reference | MSM | MSM으로서 1.5 ~2 g/day | evidence:1220 |
| 3 | 0.0122634 | ingredient_reference | 강황 추출물(터마신) | 1) 영.유아, 임산부, 수유부는 섭취에 주의 2) 강황 알레르기 체질이거나 특정질환(담낭질환 등)이 있는 분은 섭취에 주의 3) 제안된 섭취량 이상 섭취 시 소화불량, 위장장애, 메스꺼움, 위산역류 등이 있을 수 있음 | evidence:661 |
| 4 | 0.0113885 | ingredient_reference | MSM | “관절건강에 도움이 될 수 있습니다.”(기타기능 II) | evidence:1219 |
| 5 | 0.0113068 | ingredient_reference | 강황 추출물(터마신)(기능성원료인정제2014-2호) | (1) 영·유아, 임산부, 수유부는 섭취에 주의 (2) 강황 알레르기 체질이거나 특정질환(담낭질환 등)이 있는 분은 섭취에 주의 (3) 제안된 섭취량 이상 섭취 시 소화불량, 위장장애, 메스꺼움, 위산역류 등이 있을 수 있음 | evidence:2212 |

## db_167_pLQ_w6U6lx8 / c31

- 영상: https://www.youtube.com/watch?v=pLQ_w6U6lx8
- 제품명: 애터미 헤모힘
- 제품 식별: matched
- Claim: **후속적인 연구활동 지속 면역력 증진 면역 노화 개선 항암 부작용 완화 면역회복 증진**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27177
- 전체 후보: 26개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.224185 | product_direct | 애터미헤모힘 | - 헤모힘 당귀등 혼합추출물(제2006-17호) : 면역기능 개선에 도움을 줄 수 있음, 피로개선에 도움을 줄 수 있음 | products:27177/main_functionality@0:66 |
| 2 | 0.165186 | ingredient_reference | 헤모힘 당귀등 혼합추출물(기능성원료인정제2006-17호) | (국문) 면역기능 개선에 도움을 줄 수 있음 (영문) May help to improve immune function | evidence:1825 |
| 3 | 0.0730723 | product_direct | 애터미헤모힘 | 201200200752 | products:27177/manufacturing_report_number@0:12 |
| 4 | 0.0618291 | product_direct | 애터미헤모힘 | 20150522 | products:27177/registration_date@0:8 |
| 5 | 0.0428335 | product_direct | 애터미헤모힘 | 1일 2회, 1회 1포 | products:27177/intake_method@0:12 |

## db_170_2w9to5aSbYY / c01

- 영상: https://www.youtube.com/watch?v=2w9to5aSbYY
- 제품명: 애터미 헤모힘
- 제품 식별: matched
- Claim: **이 헤모힘은 한국원자력연구원에서 연구를 했고,**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27177
- 전체 후보: 26개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.0939028 | product_direct | 애터미헤모힘 | - 헤모힘 당귀등 혼합추출물(제2006-17호) : 면역기능 개선에 도움을 줄 수 있음, 피로개선에 도움을 줄 수 있음 | products:27177/main_functionality@0:66 |
| 2 | 0.0353375 | product_direct | 애터미헤모힘 | 201200200752 | products:27177/manufacturing_report_number@0:12 |
| 3 | 0.0286243 | product_direct | 애터미헤모힘 | 콜마비앤에이치(주) | products:27177/company_name@0:10 |
| 4 | 0.026002 | product_direct | 애터미헤모힘 | 20150522 | products:27177/registration_date@0:8 |
| 5 | 0.0229322 | product_direct | 애터미헤모힘 | 1. 성상 : 고유의 향미가 있고 이미, 이취가 없는 갈색의 액상 | products:27177/specification@0:36 |

## db_172_4cxxyiYdnQk / c11

- 영상: https://www.youtube.com/watch?v=4cxxyiYdnQk
- 제품명: 애터미 헤모힘
- 제품 식별: matched
- Claim: **판매원 : 애터미(주)**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27177
- 전체 후보: 26개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.30448 | product_direct | 애터미헤모힘 | - 헤모힘 당귀등 혼합추출물(제2006-17호) : 면역기능 개선에 도움을 줄 수 있음, 피로개선에 도움을 줄 수 있음 | products:27177/main_functionality@0:66 |
| 2 | 0.169638 | product_direct | 애터미헤모힘 | 콜마비앤에이치(주) | products:27177/company_name@0:10 |
| 3 | 0.109541 | product_direct | 애터미헤모힘 | 고유의 향미가 있고 이미, 이취가 없는 갈색의 액상 | products:27177/appearance@0:28 |
| 4 | 0.103742 | product_direct | 애터미헤모힘 | 1. 성상 : 고유의 향미가 있고 이미, 이취가 없는 갈색의 액상 | products:27177/specification@0:36 |
| 5 | 0.102948 | product_direct | 애터미헤모힘 | 20150522 | products:27177/registration_date@0:8 |

## db_173_go-uppdIkg0 / c11

- 영상: https://www.youtube.com/watch?v=go-uppdIkg0
- 제품명: 애터미 헤모힘
- 제품 식별: matched
- Claim: **판매원 : 애터미(주)**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27177
- 전체 후보: 26개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.30448 | product_direct | 애터미헤모힘 | - 헤모힘 당귀등 혼합추출물(제2006-17호) : 면역기능 개선에 도움을 줄 수 있음, 피로개선에 도움을 줄 수 있음 | products:27177/main_functionality@0:66 |
| 2 | 0.169638 | product_direct | 애터미헤모힘 | 콜마비앤에이치(주) | products:27177/company_name@0:10 |
| 3 | 0.109541 | product_direct | 애터미헤모힘 | 고유의 향미가 있고 이미, 이취가 없는 갈색의 액상 | products:27177/appearance@0:28 |
| 4 | 0.103742 | product_direct | 애터미헤모힘 | 1. 성상 : 고유의 향미가 있고 이미, 이취가 없는 갈색의 액상 | products:27177/specification@0:36 |
| 5 | 0.102948 | product_direct | 애터미헤모힘 | 20150522 | products:27177/registration_date@0:8 |

## db_174_Bmw8jdvxdLw / c11

- 영상: https://www.youtube.com/watch?v=Bmw8jdvxdLw
- 제품명: 애터미 헤모힘
- 제품 식별: matched
- Claim: **판매원 : 애터미(주)**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27177
- 전체 후보: 26개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.30448 | product_direct | 애터미헤모힘 | - 헤모힘 당귀등 혼합추출물(제2006-17호) : 면역기능 개선에 도움을 줄 수 있음, 피로개선에 도움을 줄 수 있음 | products:27177/main_functionality@0:66 |
| 2 | 0.169638 | product_direct | 애터미헤모힘 | 콜마비앤에이치(주) | products:27177/company_name@0:10 |
| 3 | 0.109541 | product_direct | 애터미헤모힘 | 고유의 향미가 있고 이미, 이취가 없는 갈색의 액상 | products:27177/appearance@0:28 |
| 4 | 0.103742 | product_direct | 애터미헤모힘 | 1. 성상 : 고유의 향미가 있고 이미, 이취가 없는 갈색의 액상 | products:27177/specification@0:36 |
| 5 | 0.102948 | product_direct | 애터미헤모힘 | 20150522 | products:27177/registration_date@0:8 |

## db_176_6o8pxrOwFtQ / c01

- 영상: https://www.youtube.com/watch?v=6o8pxrOwFtQ
- 제품명: 애터미 헤모힘
- 제품 식별: matched
- Claim: **쌓여가는 피로 힘이 드나요? 우리가 힘이 될게요**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27177
- 전체 후보: 26개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.0469821 | product_direct | 애터미헤모힘 | - 헤모힘 당귀등 혼합추출물(제2006-17호) : 면역기능 개선에 도움을 줄 수 있음, 피로개선에 도움을 줄 수 있음 | products:27177/main_functionality@0:66 |
| 2 | 0.00573056 | ingredient_reference | 헤모힘 당귀등 혼합추출물(기능성원료인정제2006-17호) | (1) 어린이, 임산부 및 수유부는 섭취를 피할 것 (2) 월경불순이나 출혈성 질환이 있는 여성의 경우 전문가와 상담할 것 (3) 항응고제 복용시 전문가와 상담할 것 (4) 알레르기 체질 등은 개인에 따라 과민반응을 나타낼 수 있음 (5) 이상사례 발생시 섭취를 중단하고 전문가와 상담할 것 | evidence:1827 |
| 3 | 0.0026382 | ingredient_reference | 헤모힘 당귀등 혼합추출물(기능성원료인정제2006-17호) | (국문) 면역기능 개선에 도움을 줄 수 있음 (영문) May help to improve immune function | evidence:1825 |
| 4 | 0.00213727 | product_direct | 애터미헤모힘 | 콜마비앤에이치(주) | products:27177/company_name@0:10 |
| 5 | 0.00210725 | product_direct | 애터미헤모힘 | 20150522 | products:27177/registration_date@0:8 |

## db_178_4S96NKXWpU8 / c05

- 영상: https://www.youtube.com/watch?v=4S96NKXWpU8
- 제품명: 액티브 부스터샷
- 제품 식별: matched
- Claim: **에너지**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27263
- 전체 후보: 63개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.265269 | product_direct | 액티브 부스터샷 | 판토텐산 : 지방, 탄수화물, 단백질 대사와 에너지 생성에 필요 | products:27263/main_functionality@144:179 |
| 2 | 0.250099 | product_direct | 액티브 부스터샷 | 비타민B2 : 체내 에너지 생성에 필요 | products:27263/main_functionality@268:289 |
| 3 | 0.207205 | product_direct | 액티브 부스터샷 | 비타민B1 : 탄수화물과 에너지 대사에 필요 | products:27263/main_functionality@243:267 |
| 4 | 0.20561 | product_direct | 액티브 부스터샷 | 20230530 | products:27263/registration_date@0:8 |
| 5 | 0.18513 | product_direct | 액티브 부스터샷 | 1일 1회, 1회 1병 / 뚜껑을 개봉하여 정제를 액상과 함께 섭취 또는 물과 함께 섭취하십시오. | products:27263/intake_method@0:54 |

## db_179_mnl8jo33nD4 / c05

- 영상: https://www.youtube.com/watch?v=mnl8jo33nD4
- 제품명: 야쿠르트 프로바이오틱스
- 제품 식별: matched
- Claim: **hy 프로바이오틱스 특허 18건 보유**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27439
- 전체 후보: 17개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.0445282 | product_direct | 야쿠르트 프로바이오틱스 | (주)알피바이오 | products:27439/company_name@0:8 |
| 2 | 0.042819 | product_direct | 야쿠르트 프로바이오틱스 | [프로바이오틱스] 유산균 증식 및 유해균 억제･배변활동 원활･장 건강에 도움을 줄 수 있음 | products:27439/main_functionality@0:50 |
| 3 | 0.0402424 | product_direct | 야쿠르트 프로바이오틱스 | 20210730 | products:27439/registration_date@0:8 |
| 4 | 0.033049 | product_direct | 야쿠르트 프로바이오틱스 | 200400170061268 | products:27439/manufacturing_report_number@0:15 |
| 5 | 0.0308447 | product_direct | 야쿠르트 프로바이오틱스 | 1) 성상: 고유의 향미가 있고 이미, 이취가 없는 노랑하양색의 분말 | products:27439/specification@0:38 |

## db_183_sofweMTrfjw / c11

- 영상: https://www.youtube.com/watch?v=sofweMTrfjw
- 제품명: 에버콜라겐 타임
- 제품 식별: matched
- Claim: **탱탱**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=27887
- 전체 후보: 48개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.389276 | product_direct | 에버콜라겐 타임 | (영문) May help to moisturize (dry) skin, May help to maintain good skin health by protecting against damage from UV exposure | products:27887/main_functionality@96:219 |
| 2 | 0.327679 | product_direct | 에버콜라겐 타임 | (국문) 피부 보습에 도움을 줄 수 있음, 자외선에 의한 피부손상으로부터 피부건강을 유지하는데 도움을 줄 수 있음 | products:27887/main_functionality@32:95 |
| 3 | 0.322736 | product_direct | 에버콜라겐 타임 | 제조일로부터 24개월 | products:27887/shelf_life@0:11 |
| 4 | 0.25517 | product_direct | 에버콜라겐 타임 | 20230925 | products:27887/registration_date@0:8 |
| 5 | 0.25339 | product_direct | 에버콜라겐 타임 | 고유의 향미가 있고 이미·이취가 없는 노란 하얀색의 분말 | products:27887/appearance@0:31 |

## db_188_OH4NPEmrC5Q / c02

- 영상: https://www.youtube.com/watch?v=OH4NPEmrC5Q
- 제품명: 엘레나
- 제품 식별: unmatched
- Claim: **장을 지나 질까지 도달하는**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None
- 전체 후보: 6개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.267365 | ingredient_reference | UREX 프로바이오틱스 | 유산균 증식을 통한 여성 질 건강에 도움을 줄 수 있음   (생리활성기능 2등급) | evidence:704 |
| 2 | 0.231274 | ingredient_reference | UREX 프로바이오틱스(기능성원료인정제2014-27호) | (국문) 질내 유익균 증식 및 유해균 억제에 도움을 줄 수 있음 (영문) May help to proliferate vaginal beneficial flora and to suppress pathogenic bacteria | evidence:2204 |
| 3 | 0.144316 | ingredient_reference | UREX 프로바이오틱스 | 신청원료로 9.7 mg/일 (프로바이오틱스로서 109 CFU/일 | evidence:705 |
| 4 | 0.102147 | ingredient_reference | UREX 프로바이오틱스(기능성원료인정제2014-27호) | * 유산균의 정성적 품질관리를 위해 식약처에 제시하신 방법으로 주기적으로 관리하여야 함. 또한 식약처 요청 시 시험방법 및 결과를 제출하여야 함 * [완제품 제조업체]  - 제조국 : 이탈리아, - 제조회사명 : BIOFARMA S.R.L, - 소재지 : VIA CASTELLIERE, 2-33036 MERETO DI TOMBA (UD) ※「건강기능식품의 기준 및 규격」개정고시에 따른 프로바이… | evidence:2206 |
| 5 | 0.087656 | ingredient_reference | UREX 프로바이오틱스(기능성원료인정제2014-27호) | 1,000,000,000 (CFU/일) 1,000,000,000 (CFU/일) | evidence:2205 |

## db_189__mZYh80V4l0 / c01

- 영상: https://www.youtube.com/watch?v=_mZYh80V4l0
- 제품명: 엘레나
- 제품 식별: unmatched
- Claim: **나만의 질건강 관리비법 엘레나**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_195_-RaTg6NEMZ0 / c07

- 영상: https://www.youtube.com/watch?v=-RaTg6NEMZ0
- 제품명: 엘레나 테아닌
- 제품 식별: matched
- Claim: **Stress Relief Care**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=28582
- 전체 후보: 40개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.863795 | product_direct | 엘레나 테아닌 | - 스트레스로 인한 긴장완화에 도움을 줄 수 있음 | products:28582/main_functionality@100:127 |
| 2 | 0.656216 | ingredient_reference | 테아닌(Theanine) | “스트레스로 인한 긴장을 완화시키는데 도움을 줄 수 있음” (기타기능 II) | evidence:426 |
| 3 | 0.63102 | ingredient_reference | 테아닌 | “스트레스로 인한 긴장을 완화시키는데 도움을 줄 수 있음” (기타기능 II) | evidence:455 |
| 4 | 0.278557 | product_direct | 엘레나 테아닌 | [테아닌] | products:28582/main_functionality@94:99 |
| 5 | 0.261204 | product_direct | 엘레나 테아닌 | 1) 성상: 이미, 이취가 없으며 고유의 향미가 있는 노랑 하얀색의 내용물을 함유한 하양색의 경질캡슐 | products:28582/specification@0:56 |

## db_197_X0jCGgzhae0 / c02

- 영상: https://www.youtube.com/watch?v=X0jCGgzhae0
- 제품명: 옵티머스트
- 제품 식별: matched
- Claim: **건강기능식품**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=30166
- 전체 후보: 26개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.337153 | product_direct | 옵티머스트 | (주)한국씨엔에스팜 | products:30166/company_name@0:10 |
| 2 | 0.275558 | product_direct | 옵티머스트 | 20220928 | products:30166/registration_date@0:8 |
| 3 | 0.240178 | product_direct | 옵티머스트 | [비타민D] ①칼슘과 인이 흡수되고 이용되는데 필요 ②뼈의 형성과 유지에 필요 ③골다공증발생 위험 감소에 도움을 줌 | products:30166/main_functionality@30:94 |
| 4 | 0.214923 | product_direct | 옵티머스트 | 제조일로부터 24개월 | products:30166/shelf_life@0:11 |
| 5 | 0.207879 | product_direct | 옵티머스트 | [MSM] ①관절 및 연골건강에 도움을 줄 수 있음 | products:30166/main_functionality@0:28 |

## db_201_YBn7emsawpQ / c12

- 영상: https://www.youtube.com/watch?v=YBn7emsawpQ
- 제품명: 익스트림 올인원 포 맨 스틱샷
- 제품 식별: matched
- Claim: **건강기능식품 유통판매원: (주) 익스트림**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=32493
- 전체 후보: 44개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.628566 | product_direct | 익스트림 올인원 포 맨 스틱샷 | [비타민 B6] 단백질 및 아미노산 이용에 필요, 혈액의 호모시스테인 수준을 정상으로 유지하는데 필요 | products:32493/main_functionality@192:248 |
| 2 | 0.560143 | product_direct | 익스트림 올인원 포 맨 스틱샷 | 1일 1회, 1회 1포를 섭취하십시오. | products:32493/intake_method@0:21 |
| 3 | 0.512867 | product_direct | 익스트림 올인원 포 맨 스틱샷 | 8. 비타민B6 : 표시량(15mg/20ml)의 80~150% | products:32493/specification@256:290 |
| 4 | 0.510195 | product_direct | 익스트림 올인원 포 맨 스틱샷 | 9. 비타민B1 : 표시량(12mg/20ml)의 80~180% | products:32493/specification@291:325 |
| 5 | 0.490939 | product_direct | 익스트림 올인원 포 맨 스틱샷 | 1. 성상 : 고유의 향미가 있고 이미·이취가 없는 진한 노란색 또는 노란 갈색의 액상 | products:32493/specification@0:48 |

## db_204_73yGR-979W0 / c03

- 영상: https://www.youtube.com/watch?v=73yGR-979W0
- 제품명: 천관보 프리미엄
- 제품 식별: matched
- Claim: **기능성원료 MSM과 오미자추출물의 인체적용시험 결과**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=35126
- 전체 후보: 51개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.627458 | product_direct | 천관보 프리미엄 | ①정상적인 면역기능에 필요②정상적인 세포분열에 필요,오미자추출물 : 근력 개선에 도움을 줄 수 있음 | products:35126/main_functionality@154:209 |
| 2 | 0.406988 | ingredient_reference | 오미자추출물(기능성원료인정제2016-21호) | 783 (mg) 783 (mg) | evidence:2325 |
| 3 | 0.355005 | ingredient_reference | 오미자추출물(기능성원료인정제2018-9호) | 1,582 (mg) 1,582 (mg) | evidence:2371 |
| 4 | 0.30578 | ingredient_reference | 오미자추출물(기능성원료인정제2016-21호) | (국문) 갱년기 여성 건강에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:2324 |
| 5 | 0.299028 | ingredient_reference | 오미자추출물(기능성원료인정제2018-9호) | (국문) 근력 개선에 도움을 줄 수 있음 (영문) Help to improve muscle strength | evidence:2370 |

## db_205_myFgNLXC58I / c07

- 영상: https://www.youtube.com/watch?v=myFgNLXC58I
- 제품명: 천관보 프리미엄
- 제품 식별: matched
- Claim: **정상적인 면역기능 아연**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=35126
- 전체 후보: 51개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.889921 | product_direct | 천관보 프리미엄 | 아연 : 정상적인 면역 기능에 필요 | products:35126/main_functionality@327:346 |
| 2 | 0.829823 | product_direct | 천관보 프리미엄 | 6) 아연 : 표시량의 80~150% (표시량 : 8.5mg/70ml) | products:35126/specification@204:243 |
| 3 | 0.780668 | product_direct | 천관보 프리미엄 | ①정상적인 면역기능에 필요②정상적인 세포분열에 필요,오미자추출물 : 근력 개선에 도움을 줄 수 있음 | products:35126/main_functionality@154:209 |
| 4 | 0.409639 | product_direct | 천관보 프리미엄 | ①단백질 및 아미노산 이용에 필요②혈액의 호모시스테인 수준을 정상으로 유지하는데 필요 | products:35126/main_functionality@105:152 |
| 5 | 0.367188 | product_direct | 천관보 프리미엄 | 1일 1회, 1회 1포(1포당 70ml)를 그대로 섭취하십시오. | products:35126/intake_method@0:35 |

## db_207_2gBANzYTC5U / c22

- 영상: https://www.youtube.com/watch?v=2gBANzYTC5U
- 제품명: 청인 퓨어 MSM
- 제품 식별: matched
- Claim: **GMP**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=35477
- 전체 후보: 23개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.341827 | product_direct | 청인 퓨어 MSM | (주)힐링바이오 | products:35477/company_name@0:8 |
| 2 | 0.340805 | product_direct | 청인 퓨어 MSM | 3. 중금속 | products:35477/specification@93:99 |
| 3 | 0.300721 | product_direct | 청인 퓨어 MSM | 1. 성상 : 이미, 이취가 없고 고유의 향미가 있는 백색의 분말을 함유한 미황색의 경질캡슐 | products:35477/specification@0:51 |
| 4 | 0.297085 | product_direct | 청인 퓨어 MSM | - 카드뮴(mg/kg) : 0.1이하 | products:35477/specification@121:141 |
| 5 | 0.262616 | product_direct | 청인 퓨어 MSM | - 납(mg/kg) : 0.1이하 | products:35477/specification@101:119 |

## db_208_0drznbKPJgc / c01

- 영상: https://www.youtube.com/watch?v=0drznbKPJgc
- 제품명: 총총
- 제품 식별: unmatched
- Claim: **우리아이 건강친구 총총**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_210_NKyAOi6Hrg8 / c02

- 영상: https://www.youtube.com/watch?v=NKyAOi6Hrg8
- 제품명: 코어틴 그린프로틴
- 제품 식별: unmatched
- Claim: **모델 : ‘미스트롯2’ 진 양지은**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None

**연결 가능한 Evidence 없음**

## db_211_L4KfNfwGB1s / c13

- 영상: https://www.youtube.com/watch?v=L4KfNfwGB1s
- 제품명: 콜라겐 히알루론산 앰플샷
- 제품 식별: unmatched
- Claim: **비타민 B₆ 1.5mg**
- 식별 경로/사유: exact_name / known_identity_conflict; product_id=None
- 전체 후보: 41개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.264388 | ingredient_reference | 히알루론산 | 피부 보습에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:632 |
| 2 | 0.258314 | ingredient_reference | 히알루론산 | 자외선에 의한 피부손상으로부터 피부 건강 유지에 도움을 줄 수 있음(생리활성기능 2등급) | evidence:623 |
| 3 | 0.171955 | ingredient_reference | 히알루론산 | - | evidence:625 |
| 4 | 0.160323 | ingredient_reference | 히알루론산 | 1) 임산부, 수유부는 섭취에 주의 2) 알레르기 체질 및 특이체질, 질병치료 중인 사람은 섭취에 주의 | evidence:634 |
| 5 | 0.137505 | ingredient_reference | 히알루론산 | “피부 보습에 도움을 줄 수 있습니다.(기타Ⅱ)” | evidence:337 |

## db_212_qbQfBqPEqGQ / c16

- 영상: https://www.youtube.com/watch?v=qbQfBqPEqGQ
- 제품명: 토비콤 아이포커스
- 제품 식별: matched
- Claim: **판매원 : 안국약품(주)**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=38148
- 전체 후보: 44개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.343562 | product_direct | 토비콤 아이 포커스 | 고유의 향미가 있고 이미, 이취가 없는 어두운 빨간색의 내용물을 함유한 흑갈색의 타원형 연질캡슐 | products:38148/appearance@0:53 |
| 2 | 0.32502 | product_direct | 토비콤 아이 포커스 | 1) 성상 : 고유의 향미가 있고 이미, 이취가 없는 어두운 빨간색의 내용물을 함유한 흑갈색의 타원형 연질캡슐 | products:38148/specification@0:61 |
| 3 | 0.295953 | product_direct | 토비콤 아이 포커스 | [비타민 B12] | products:38148/main_functionality@222:231 |
| 4 | 0.289125 | product_direct | 토비콤 아이 포커스 | 1일 1회, 1회 1캡슐을 충분한 물과 함께 섭취하십시오. | products:38148/intake_method@0:32 |
| 5 | 0.27559 | product_direct | 토비콤 아이 포커스 | [비타민 B1] | products:38148/main_functionality@111:119 |

## db_214_bhFZouAiiGc / c01

- 영상: https://www.youtube.com/watch?v=bhFZouAiiGc
- 제품명: 트루바이타민
- 제품 식별: matched
- Claim: **모델의 인터뷰영상입니다.**
- 식별 경로/사유: exact_name / unique_candidate_without_known_identity_conflict; product_id=38286
- 전체 후보: 51개. 아래는 상위 5개.

| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 0.022499 | product_direct | 트루바이타민 | (1) 정제1(노랑주황색정제) : 고유의 향미가 있고 이미, 이취가 없는 점박이가 있는 노랑주황색 원형 제피정제 (2) 정제2 (노란하양색정제) : 고유의 향미가 있고 이미, 이취가 없는 노란 하양색 타원형 제피정제 (3) 연질캡슐 (빨강색연질캡슐) : 고유의 향미가 있고 이미, 이취가 없는 연한 노란 연두색의 점도가 있는 내용물을 함유한 빨강색의 타원형 연질캡슐 | products:38286/appearance@0:204 |
| 2 | 0.0189801 | product_direct | 트루바이타민 | [비타민D] ①칼슘과 인이 흡수되고 이용되는데 필요②뼈의 형성과 유지에 필요③골다공증발생 위험 감소에 도움을 줌 | products:38286/main_functionality@442:504 |
| 3 | 0.0171801 | product_direct | 트루바이타민 | (주)비오팜 | products:38286/company_name@0:6 |
| 4 | 0.0161436 | product_direct | 트루바이타민 | ①성상 : 고유의 향미가 있고 이미, 이취가 없는 노란 하양색 타원형 제피정제 | products:38286/specification@430:473 |
| 5 | 0.0154781 | product_direct | 트루바이타민 | ①성상 : 고유의 향미가 있고 이미, 이취가 없는 점박이가 있는 노랑주황색 원형 제피정제 | products:38286/specification@18:67 |

## db_217_SHhSMRCCVEM / c02

- 영상: https://www.youtube.com/watch?v=SHhSMRCCVEM
- 제품명: TruVitamin X™
- 제품 식별: unmatched
- Claim: **비타민의 본질에 충실한 비타민**
- 식별 경로/사유: full_name_damerau_levenshtein / manufacturer_missing_for_typo_route; product_id=None

**연결 가능한 Evidence 없음**
