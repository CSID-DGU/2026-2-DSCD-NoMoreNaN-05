# 제품 기능성 전달 JSON

`data/processed/product_functionality_handoff/mapped_products.json`을 기본 전달 파일로 사용함. 제품 하나를 선택한 238개 영상 내 제품 항목과 여기에 속한 원본 Claim 2,912개를 포함함.

요청 형식을 유지하면서 `url`, `product_ref`를 추가함. 한 영상에 여러 제품이 있으면 제품별 레코드로 분리하고 해당 product_ref의 Claim만 담음. Claim 원문/필드는 수정하지 않음. `evi_product`는 실제 DB의 product_id, product_name, company_name, manufacturing_report_number, main_functionality를 그대로 사용함. `db_version`은 dataset_registry에서 dataset_key=products 행의 loaded_at인 2026-09-20T09:51:18Z임.

기본 파일의 상태는 confirmed 113개, unresolved 125개임. 단일 검색 결과라도 제조사 정보가 없거나 불일치하면 요청한 상태 정의에 맞춰 unresolved로 기록하고 후보 제품의 evi_product를 제공함. confirmed는 설정된 제품명/제조사 비교 또는 실제 신고번호 비교 규칙을 통과했다는 의미이며 사람의 독립 검증이나 Claim 사실 판정을 의미하지 않음. name_and_company는 제품명 정확 일치 외에 기록된 브랜드 분리/거리 기준을 포함할 수 있어 note에 검색 경로와 점수를 표시함. DB에서 가져온 신고번호만으로 report_number라고 표시하지 않음.

`confirmed_products.json`: confirmed만 분리한 113개 레코드, Claim 1,513개.

`all_results.json`: 미선택/검색 실패 및 product_ref 미해결 Claim까지 포함한 전체 이력. 총 295개 레코드, 원본 3,400개 Claim을 누락/중복 없이 보존함. 복수 후보 미선택은 evi_product=null과 product.candidates 배열로 표시함. 제품 하나를 고르지 못한 상황에서 첫 후보를 임의 지정하지 않음.

`summary.json`: 파일별 집계 및 입력 해시. 입력 SHA256 확인, 원본 Claim 보존, 기능성 DB 원문 일치 검증을 수행함. 관련 회귀 테스트 총 37개 통과함. 원료 검색 및 모델 추론을 실행하지 않음.

재생성:

```powershell
.\.venv\Scripts\python.exe scripts/export_product_functionality_handoff.py
```

이 스크립트는 현재 저장된 제품 매핑과 동일한 입력 해시인 경우만 내보냄. 새로운 입력은 먼저 제품 후보 검색과 제조사 구분을 실행해야 함.
