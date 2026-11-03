# claims_all_real.json 제품 매핑 및 전달 JSON

입력: 사용자가 제공한 claims_all_real.json. 412개 영상, 1,066개 제품 항목, 9,638개 Claim. 기존 입력과 결과를 덮어쓰지 않음.

기존 90.7% 후보 검색 시험과 같은 제품명 정확 일치, 관찰된 브랜드명 분리 후 정확 일치, 기존 식별 결과, 전체 이름 Damerau–Levenshtein 80점 이상 검색을 적용함. 후보 여러 개는 제조사 원문 → 공장 표기 정리 → 승인 PAIR로 구분함. 확인된 신고번호 충돌은 무시하지 않음. 90.7%는 이전 입력의 결과이며 새 입력에 보장되는 수치가 아님.

## 새 입력 결과

- 후보 검색: 773개 / 1,066개 = 72.5%.
- 단일 후보: 661개. 복수 후보: 112개. 후보 없음: 293개.
- 복수 후보 중 제조사로 추가 구분: 13개.
- 단일 제품 선택: 674개 / 1,066개 = 63.2%.
- 선택된 제품에 속한 Claim: 6,317개.
- 선택 결과의 status: confirmed 65개, unresolved 609개. 제조사 미확인/불일치가 허용된 단일 후보를 confirmed로 표시하지 않음.
- 전체 결과에는 원본 Claim 9,638개가 누락/중복 없이 보존됨. 입력 제품에 대응하지 않는 product_ref의 Claim 249개도 별도 레코드에 보존됨.

## 파일

`data/processed/product_functionality_handoff_real/`

- `mapped_products.json`: 전달용. 선택된 제품 674개와 해당 Claim. product.evi_product.main_functionality는 DB 원문임. 원본 video_id, url, product_ref와 Claim 필드를 보존함.
- `all_results.json`: 미연결/복수 후보/제품 참조 미해결을 포함한 전체 결과. 복수 후보를 임의로 선택하지 않고 candidates 배열에 저장함.
- `confirmed_products.json`: confirmed만 모은 결과.
- `product_matches.json`: 검색 경로·점수·후보·제조사 비교 등 상세 기록.
- `summary.json`: 집계 및 입력/DB/규칙 설정 SHA256.
- `source_input.json`: 원본 입력 사본.

새 입력을 받는 독립 실행 스크립트를 추가하고 관련 회귀 테스트 41개가 통과함. DB는 읽기 전용으로 접근하며 원본 입력/Claim과 DB 필드 일치를 검증함. API 호출·원료 검색·임베딩·재순위 추론은 실행하지 않음. 연결률은 정답 정확도와 다름.

```powershell
.\.venv\Scripts\python.exe -u -X utf8 scripts/map_claim_products.py --input "C:\Users\박이정\Documents\카카오톡 받은 파일\claims_all_real.json" --output-dir data/processed/product_functionality_handoff_real
```
