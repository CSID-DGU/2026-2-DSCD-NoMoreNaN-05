# claims_all_y_final.json 제품 매핑

입력: 535개 영상(URL 535개), 제품 항목 1,302개, Claim 8,728개. 원본 입력과 이전 결과를 수정하지 않음.

## 적용 규칙

제품명 정확 일치 → 관찰된 브랜드명 분리/재결합 → 기존 식별 결과 → 전체 이름 Damerau–Levenshtein 70점 이상 검색. 제조사는 원문 → 공장·사업부 정리 → 승인 PAIR 10개로 구분하며, PAIR는 정확한 이름 경로에 한정함. 신고번호 충돌은 허용하지 않음.

추가로 상표기호·Unicode·한자(한글) 병기·DB 영문 별칭을 비교함. 소수점/숫자 범위·단위·+·%는 보존함. 표기 정리 후 정확한 제품이 있으면 이전의 유사도 후보보다 우선함. 축약 이름은 브랜드를 유지한 단어 경계/구절로 검색함. 일반 원료명이나 '키즈' 같은 표현만으로 다른 브랜드의 제품을 연결하지 않음.

누락 이름은 같은 product_ref의 Claim, 캐시된 영상 제목·설명, 공개 oEmbed 제목, 썸네일 OCR로 보완함. 제목만으로 여러 제품 참조에 같은 제품을 임의 배정하지 않음. 새로운 복원 후보는 모두 검토 대상으로 기록함. 영상 전체 다운로드·전체 프레임 OCR·ASR은 수행하지 않음.

공개 제목 76개를 추가 조회함. 새 썸네일 111장에 한국어 OCR을 실행하고 기존 OCR 2건을 재사용함. OCR 결과에서 제품명으로 독립 연결된 항목은 없었음.

## 결과

| 기준 | 후보 연결 | 제품 하나 선택 |
|---|---:|---:|
| 영상별 제품 항목 1,302개 | 1,060개 (81.4%) | 785개 (60.3%) |
| 제품명+브랜드 중복 제거 510개 | 434개 (85.1%) | 330개 (64.7%) |

중복 제거는 NFC·대소문자·공백을 정리한 입력 제품명+브랜드 키를 사용함. 같은 키에서 한 건이라도 검색/선택되면 연결된 그룹으로 집계함. 제품명이 없는 113개 항목은 중복 제거 집계에서 제외함. 서로 다른 이름이 같은 DB 제품으로 연결될 수 있으므로 DB 고유 제품 수와 다름. 위 비율은 정확도가 아님.

70점+브랜드 재결합 기본 후보 1,040개에서 추가 복원 20개로 1,060개가 됨. 추가 경로: 구절 검색 5개, 영상에서 관찰한 영문/한글 대응 1개, 같은 제품 Claim에서 이름 복원 10개, 영상 제목·설명 3개, 표기/DB 영문 별칭 1개. 별도로 기존 유사도 검색 8개 항목은 정확한 표기 후보로 재정리함.

## 전달 파일

`data/processed/product_functionality_handoff_y_final/mapped_products.json`

- 영상 URL 407개, 영상별 제품 항목 785개, DB 고유 제품 283종, Claim 5,273개.
- product.evi_product.main_functionality는 DB 원문. URL·Claim 원문을 보존함.
- 단일 후보를 선택했더라도 동일성 미확인 항목은 unresolved로 유지함.

`all_results.json`에는 미연결·복수 후보·입력 제품 참조 미해결을 포함한 원본 Claim 8,728개가 누락/중복 없이 보존됨. `product_matches.json`, `recovered_candidates.json`, `notation_refinements.json`, `summary.json`에 검색 경로·점수·출처·집계를 기록함.

원본 Claim 전체 보존, DB 기능성 원문 일치, 입력 SHA256을 검증함. 관련 회귀 테스트 41개 통과함. Evidence/원료 검색 및 임베딩/재순위 추론을 실행하지 않음.

## 재실행

```powershell
.\.venv\Scripts\python.exe -u -X utf8 scripts/map_claim_products.py --input "C:\Users\박이정\Documents\카카오톡 받은 파일\claims_all_y_final.json" --threshold 70 --brand-recombine --output-dir data/processed/product_functionality_handoff_y_final/base70
.\.venv\Scripts\python.exe -X utf8 scripts/build_recovery_metadata.py --base-dir data/processed/product_functionality_handoff_y_final/base70 --fetch-missing
.\.venv\Scripts\python.exe -X utf8 scripts/fetch_recovery_thumbnails.py --base-dir data/processed/product_functionality_handoff_y_final/base70 --mapping-dir data/processed/product_functionality_handoff_y_final/base70
.\scripts\ocr_recovery_thumbnails.ps1 -Folder "$PWD\data\processed\product_functionality_handoff_y_final\base70\recovery_thumbnails"
.\.venv\Scripts\python.exe -X utf8 scripts/build_recovery_metadata.py --base-dir data/processed/product_functionality_handoff_y_final/base70 --attach-ocr
.\.venv\Scripts\python.exe -u -X utf8 scripts/recover_product_candidates.py --base-dir data/processed/product_functionality_handoff_y_final/base70 --output-dir data/processed/product_functionality_handoff_y_final --prefer-notation
```
