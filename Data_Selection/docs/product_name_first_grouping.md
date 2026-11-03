# 제품명 우선·신고번호 보조 규칙

사용자 수정 지시: 제품명/제조사 연결이 우선이며, 신고번호는 제품명 경로에서 연결하지 못했을 때 보조 조회에 사용함. 제품명과 신고번호가 모두 일치해야 하는 조건으로 사용하지 않음. 제품명으로 한 그룹을 고를 수 있으면 입력 신고번호가 다르다는 이유로 제외하지 않음.

같은 정규화 DB 제품명 + 공장/사업부 표기를 제외한 제조사(승인 PAIR 포함)를 하나의 검색용 제품 그룹으로 묶음. 서로 다른 제품명·숫자·버전은 같은 제조사라는 이유로 합치지 않음. 제조사가 없는 DB 행끼리는 임의 그룹화하지 않음.

예: 관절엔 콘드로이친 1200 / 콜마비앤에이치 음성공장과 세종3공장을 하나의 제품 그룹으로 연결함. 신고번호가 다른 두 DB 행과 두 기능성 원문은 모두 보존함.

## 현재 결과

claims_all_y_final.json의 제품명·브랜드 중복 제거 510개 기준, 단일 그룹 연결은 기존 330개(64.7%)에서 339개(66.5%)로 증가함. 후보 연결은 434개(85.1%)로 유지됨.

영상별 제품 항목 기준으로는 1,302개 중 812개(62.4%)가 선택됨. 기존 785개 대비 27개 추가 연결됨. 이번 입력에는 신고번호가 제공된 항목이 0개이므로, 증가분은 공장·신고기록별 DB 행을 한 제품 그룹으로 묶은 결과임. 정답 정확도는 측정하지 않음.

## 전달 JSON

`data/processed/product_functionality_handoff_y_final_name_first/mapped_products.json`

- URL 421개, 영상별 제품 항목 812개, 검색용 DB 제품 그룹 290개, Claim 5,468개.
- `evi_product`는 그룹의 대표 실제 DB 행임. 신고번호로 특정한 유일 행이라는 의미가 아님.
- 같은 그룹의 원본 DB 행은 `product.group_records`, 모든 DB ID/신고번호는 `product.group`, 기능성 원문은 `product.main_functionality_sources`에 보존함.
- 대표 행은 최소 product_id로 재현 가능하게 정하며, 신고번호 fallback이면 실제 일치 행을 대표로 사용함. evi_product의 필드/기능성은 실제 DB 원문을 수정하지 않음.
- `all_results.json`에는 원본 Claim 8,728개 전체를 보존함. 입력/DB/이전 파일은 변경하지 않음.

현재 결과 재생성: `.\.venv\Scripts\python.exe scripts/apply_name_first_product_groups.py`

새 입력은 `scripts/map_claim_products.py`로 이름 우선 후보를 새로 생성함. 기본값은 신고번호 fallback 정책임. `--strict-report-match`는 과거 조건을 재현하기 위한 옵션임. 복원 단계 후 `apply_name_first_product_groups.py --base-dir <result-directory> --output-dir <new-directory>`를 실행함.

관련 테스트 48개 통과함. 제품명 성공/신고번호 불일치, 이름 실패/신고번호 일치, 같은 제품명·제조사의 공장/신고번호 차이, 다른 제품명 유지, 제조사 미확인 행의 무분별 병합 방지를 검증함.
