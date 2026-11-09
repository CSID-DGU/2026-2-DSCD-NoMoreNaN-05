# 제품 후보의 DB 정보까지 포함한 전달본 v2

기존 `exports/claim_type_db_20261103/claims_with_db.json`을 대체하여 사용할 새 사본임.
원본 입력・기존 전달본・SQLite는 수정하지 않음. Claim 원문과 effect를 보존하고 ETC만 제외함.

## 결과

- 기존 집계 기준(제품명・브랜드 중복 제거, 브랜드 존재): 501개 중 429개, 85.63% 후보 연결.
- 전체 이름 존재 제품 기준: 510개 중 435개, 85.29% 후보 연결.
- 영상별 제품 항목: 1,302개 중 1,061개에 후보 DB 전달. 나머지 241개는 not_found.
- ETC 제외 Claim: 7,487개 중 5,969개에 제품 후보 DB 연결, 79.72%.
- 연결되지 않은 1,518개: 제품 not_found에 속한 1,305개 + product_ref 참조 실패 213개.
- 연결 Claim에는 PERSON_CREDENTIAL 36개도 있음. 네 가지 DB 비교 타입만 대상으로 하면 5,933개임.
- unresolved로 남기며 후보 DB를 삭제하는 처리는 없음.

## 수신 코드에서 반드시 바꿀 부분

1. `match.status == "confirmed"`만 통과시키던 조건을 제거함.
2. `match.status == "matched"`이면 `candidate_products`의 각 후보 DB를 읽음.
3. 최상위 `product.DB`가 null이어도 candidate_products가 있으면 연결된 자료가 있는 것임.
4. Claim.product_ref와 같은 영상 products의 product_ref로 연결함. 다른 제품을 대신 사용하지 않음.
5. 후보별로 독립해서 비교하고 제품 ID・회사・신고번호를 결과의 근거에 남김.
6. 후보 자료를 합쳐 한 제품의 성분 목록인 것처럼 취급하지 않음. 후보에 따라 결론이 달라지면 그 차이를 표시함.

`matched`는 보유 DB에서 제품 후보가 연결되었다는 뜻임. 광고 제품과의 동일성 또는 Claim의 진실을 검증했다는 뜻은 아님.
따라서 기존 상태를 단순히 전부 confirmed로 바꾸지는 않았음.

## 구조

```text
video
  products[]
    product_ref
    product_name, brand_name, manufacturer_name (입력 원문)
    manufacturing_report_number (입력 원문 유지)
    match.status: matched / not_found
    match.candidates: 실제로 DB를 붙여 전달한 후보 행 수
    match.selection_reason: 우선 후보 선택 또는 선택하지 않은 이유
    match.identity_confirmed: false (이 출력의 목적은 후보 근거 전달)
    preferred_product_id: 회사 우선순위 등으로 한 행을 고를 수 있을 때만 값
    DB: 우선 후보의 타입별 DB 사본, 우선 후보가 없으면 null
    candidate_products[]
      product_id, product_name, company_name, manufacturing_report_number
      DB
        QUANTITY / COMPOSITION / CERTIFICATION / EFFECT
  claims[]: ETC를 제외한 원본 Claim, effect 보존
```

우선 후보 선택은 입력 manufacturer_name이 있으면 그 값과 DB company_name을 먼저 비교하고,
없으면 brand_name을 보조 비교함. 법인・공장 표기 정리와 정확 제품명 경로의 승인 PAIR를 사용함.
제조사 충돌이 있으면 우선 후보를 강제로 고르지 않지만 검색된 각 후보의 DB는 그대로 제공함.
예전 선택 결과가 있더라도 그것만으로 우선 후보를 강제하지 않음.
여러 공장・신고번호 행이 있으면 원본별 DB를 따로 보존함.

## 읽기 예제

```python
import json

with open('claims_with_db.json', encoding='utf-8') as f:
    videos = json.load(f)

for video in videos:
    products = {p['product_ref']: p for p in video['products']}
    for claim in video['claims']:
        product = products.get(claim.get('product_ref'))
        candidates = product.get('candidate_products', []) if product else []
        for candidate in candidates:
            db_for_claim = candidate['DB'].get(claim['claim_type'])
            if db_for_claim is None:
                continue  # PERSON_CREDENTIAL 등 타입별 비교 자료 없음
            # 이 Claim과 candidate 하나의 db_for_claim을 비교함.
            # 후보 product_id도 판정 근거에 함께 기록함.
```

파이썬 실행 코드가 있는 환경에서는
`from scripts.export_candidate_db_handoff import iter_claim_contexts`를 사용할 수 있음.

파일:
- claims_with_db.json: 새 전달본 전체.
- summary.json: 집계・범위・원본 해시.
- claim_candidate_index.json: Claim별 후보 제품 ID 목록 및 참조 실패 기록.

재생성: `python scripts/export_candidate_db_handoff.py`
