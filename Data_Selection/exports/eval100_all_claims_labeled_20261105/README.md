# 100편 전체 Claim 정답 라벨 및 전달 형식

## 사용할 파일
- claims_with_db_labeled.json: 전체 1554개 Claim에 gold_label을 추가한 평가 정답 합본.
- claims_with_db.json: 정답을 보지 않고 A·B를 실행할 입력. 앞서 전달한 입력과 바이트 단위로 동일함.
- gold_labels_all_1554.json: (video_id, claim_id)별 정답·제품·DB 근거·review_note.
- two_product_videos_10_labeled.json: 제품 2개 영상 10편의 전체 필드와 정답.
- videos_labeled / videos_input: 동일 데이터를 영상별 100개로 분리. 합본과 중복 실행하지 않음.
- handoff_labeled_100.zip: 라벨 포함 합본. handoff_A_B_input_100.zip: 정답 없는 영상별 판정 입력.

## 인터페이스
기존 root video_id/url/db_version/products/claims 유지. 제품 원본 필드 + match + DB 유지.
confirmed/unresolved/not_found 의미와 report_number/name_and_company 값을 변경하지 않음.
이번 110개 제품은 기존 선정 단계부터 모두 confirmed이며 DB가 채워져 있음. 후보 성공을 확정으로 승격한 것이 아님.
products[].DB만으로 모든 선정 제품의 타입별 근거를 읽을 수 있음. candidate_products 또는 matched 상태는 없음.
claim_type 배열은 사용자가 수신 측 처리 가능을 확인한 형식을 유지함.
effect를 포함한 원본 8개 Claim 필드는 값까지 유지하며, 라벨 파일에는 요청한 gold_label 하나만 추가함.
EFFECT Claim 중 원본 effect:null인 87개도 값을 임의로 생성하지 않고 그대로 보존함. original_EFFECT_null_values.json에서 목록을 확인할 수 있음.
수신 B가 effect 값만 사용하면 이 87개가 누락될 수 있음. 요구사항의 Claim 원문인 text를 이용하는지 수신 측 확인이 필요함.
DB 중 RAWMTRL_STD_INFO/RAWMTRL_DICT_INFO/RAWMTRL_CLASS_INFO는 배열, 나머지는 문자열을 유지함.
추가 금지 상태를 회피하려고 unresolved에 후보 DB를 넣거나 임의 제품을 확정하지 않음.

## 라벨링 범위와 해석
ETC 제외 후 기존 1424개 + 합성 130개, 총 1554개를 승인된 여섯 라벨로 판단함.
주간 발표 및 사용자가 승인한 기준표를 적용함. 구현 PDF 1쪽의 근거 없는 효능=VIOLATION은 적용하지 않음.
근거 없는 효능은 과장까지 있으면 OVERCLAIM, 아니면 UNCLEAR. 질병·의약품 또는 명확한 DB 충돌은 VIOLATION.
원본의 잘못된 product_ref·계열 제품 혼합·제품 버전 가능성은 다른 제품 자료를 대신 쓰지 않고 UNCLEAR로 남김.
복합 문장의 확인 가능한 부분만 보고 전체를 SUPPORTED로 처리하지 않음. 미확인 핵심 주장이 남으면 UNCLEAR.
숫자 차이는 같은 단위·기준량인지 확인하며 균수 최소 규격·포장량·원료 인정량을 제품 실함량과 혼동하지 않음.
최종 사용자 승인 기준표를 우선하여 포장 규격·총량·개수 및 상표·독자 배합명은 UNCLEAR로 처리함. 구현 PDF 일부의 OUT_OF_SCOPE 분류와 구분함.
GMP는 문서에 따른 업종 간접 확인. 인허가일을 회사 설립일 또는 브랜드 업력으로 사용하지 않음.
전부 assistant가 작성한 평가 정답 초안이며 독립된 사람 간 합의나 법적 확정이 아님.
NLI 점수나 A·B 출력을 정답으로 쓰지 않았고 실제 A·B 수신 프로그램 실행은 검증하지 못함.
원본 영상 미디어를 보지 않고 전달된 Claim 원문·제품 DB를 비교했으므로 원본 추출 오류를 확정 교정하지 않음.
주간 발표의 집계/모델 확률과 비교하는 평가이지, 이 정답을 모델 예측 특징으로 전달하지 않음.

## 라벨 개수
| 라벨 | 전체 | 기존 | 합성 |
|---|---:|---:|---:|
| DISCLAIMER | 25 | 25 | 0 |
| OUT_OF_SCOPE | 330 | 330 | 0 |
| OVERCLAIM | 66 | 1 | 65 |
| SUPPORTED | 587 | 587 | 0 |
| UNCLEAR | 476 | 476 | 0 |
| VIOLATION | 70 | 5 | 65 |

## 보조 수치 자료
별표5 기준치 참고: https://www.law.go.kr/flDownload.do?bylClsCd=110201&flSeq=136815111&gubun=
비타민D 단위 환산 참고: https://ods.od.nih.gov/factsheets/Vitamind-HealthProfessional/
이 외부 자료는 평가 메모의 단위·비율 검산에만 쓰며 기존 DB 필드에는 추가하지 않음.
