# Claim Verification SQLite 구조

## 1. 파일과 테이블의 대응

| 원본 파일 | 적재 테이블 | 적재 기준 |
| --- | --- | --- |
| `health_functional_food_products.jsonl` | `products` | 제품 한 행을 `products` 한 행으로 저장. `main_functionality`는 공식 비교 정보로 보존 |
| `functional_ingredient_status.txt` | `ingredients`, `evidence` | 원료 인정현황의 원료 한 행을 `FUNCTIONAL_INGREDIENT`로 분류 |
| `individually_approved_ingredient_info.txt` | `ingredients`, `evidence` | 개별인정형 원료 한 행을 `INDIVIDUALLY_APPROVED`로 분류 |
| `disease_codes.jsonl` | `diseases` | 질병코드·상병구분·의료구분 조합 한 행을 저장 |

원본 파일은 이 폴더에 보존한다. SQLite에는 검색·조인·검증에 필요한 구조화 컬럼만 넣고, 큰 원문 JSON은 중복 저장하지 않는다.

## 2. 테이블별 역할

### `dataset_registry`

어떤 원본 파일을 언제 읽었고 몇 건을 적재했는지 기록한다. DB 재생성 뒤 데이터 범위를 확인하는 용도다.

### `products`

건강기능식품 제품 마스터다. `product_id`는 DB 내부 식별자이며, 제조신고번호, 제품명, 회사명, 등록일, 기능성 내용, 섭취방법·주의사항·규격을 저장한다.

- 검색 키: `manufacturing_report_number`, `product_name_normalized`
- 제품명만으로 원료를 확정하지 않는다. 제품 원료 목록이 현 데이터에 없기 때문이다.

### `ingredients`

공식적으로 인정된 원료 마스터다.

| `ingredient_type` | 출처 | 주요 값 |
| --- | --- | --- |
| `FUNCTIONAL_INGREDIENT` | 기능성 원료 인정현황 | 인정번호, 원료명, 기능성 내용, 일일섭취량, 주의사항, 업체·허가일 |
| `INDIVIDUALLY_APPROVED` | 개별인정형 원료정보 | 인정번호, 원료명, 주기능성, 일일섭취 최소·최대량, 주의사항 |

원료명과 인정번호로 검색 인덱스를 만든다. 원료명이 같은 여러 인정번호는 보존하며 임의로 합치지 않는다.

### `diseases`

질병 표준 사전이다. `disease_code`, 국문·영문 질병명, 상병구분(`sick_type`), 의료구분(`medicine_type`)을 저장한다. 같은 질병코드라도 상병구분과 의료구분이 다르면 별도 레코드로 보존한다.

### `claims`

광고 영상에서 추출한 검증 대상 문장을 저장한다. 현재 원본 검증 데이터만 적재한 단계이므로 비어 있다.

- `claim_origin`: `VIDEO` 또는 `MANUAL`
- `product_id`: 관련 제품이 확인됐을 때 연결하는 외래키
- `subject_text`, `predicate_text`, `target_text`, `disease_id`: 영상 STT/OCR 또는 LLM 추출 단계에서 채움

즉, claim은 **판정 결과가 아니라 광고 영상에서 추출한 검증 대기 문장**이다.

### `evidence`

원료별 공식 근거 문장을 저장한다. 한 원료에서 아래처럼 여러 근거가 생길 수 있다.

- `OFFICIAL_FUNCTIONALITY`: 공식 기능성 내용
- `OFFICIAL_INTAKE`: 공식 일일 섭취량 또는 최소·최대 섭취량
- `OFFICIAL_PRECAUTION`: 공식 섭취 주의사항

각 근거는 `ingredient_id` 외래키로 원료에 연결되며, 현재 출처 권한은 `MFDS`다.

### `claim_evidence_links`

claim과 근거를 연결하고 판정 결과를 저장하는 테이블이다. 현재 자동 매칭을 하지 않았으므로 비어 있다.

| 컬럼 | 의미 |
| --- | --- |
| `match_method` | `EXACT`, `RULE`, `LLM`, `MANUAL` 중 연결 방식 |
| `verdict` | `SUPPORTED`, `CONTRADICTED`, `INSUFFICIENT`, `REVIEW_REQUIRED` |
| `confidence` | 0~1 신뢰도. 수동 판정은 비워둘 수 있음 |
| `reason` | 판정 근거 요약 |

## 3. 정규화·매핑 규칙

### 이름 정규화

제품명·원료명·질병명 검색을 위해 `*_normalized` 컬럼을 만들었다. 공백, 하이픈, 밑줄, 쉼표, 마침표, 괄호, 대괄호를 제거하고 소문자화한다.

```text
"홍삼-추출물 (분말)" → "홍삼추출물분말"
```

이 값은 후보 검색용이다. 이름이 같다는 이유만으로 자동으로 사실 판정을 확정하지 않는다.

### 현재 적용한 매핑

1. 제품정보 → 제품: 원본 한 행을 `products` 한 행으로 직접 적재
2. 원료 인정정보 → 근거: 원료별 기능성·섭취량·주의사항을 각각 `evidence` 행으로 분리
3. 질병코드 → 질병 사전: 코드·상병구분·의료구분 조합을 보존
4. 광고 영상 claim → claim: 다음 단계에서 STT/OCR·LLM 추출 결과를 저장

### 아직 하지 않은 자동 매핑

현재 데이터에는 제품별 원료 성분표가 없고, claim 문장도 대상 질병·용량·표현 강도가 구조화되지 않았다. 따라서 `products → ingredients`, `claims → evidence`, `claims → diseases`를 지금 자동으로 연결하면 오탐이 생긴다.

다음 단계에서 claim에서 원료명·질병명·기능성 표현·용량을 추출하고, 아래 순서로 연결한다.

```text
정규화된 원료명/인정번호 정확 일치
  → 기능성 표현 규칙 비교
  → 질병코드 사전 후보 연결
  → LLM 또는 사람 검토
  → claim_evidence_links에 판정·이유·신뢰도 기록
```

## 4. VS Code 조회용 DB

`claim_verification_browser.sqlite`는 VS Code에서 보기 쉽게 만든 32MB 읽기용 사본이다.

- 제품·원료·질병·근거의 핵심 컬럼과 전체 레코드는 유지
- `claims`는 광고 영상 claim 적재 전까지 빈 테이블
- 판정·추가 입력에는 원본 `claim_verification.sqlite`를 사용
