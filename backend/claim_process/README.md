# Claim Process

| 폴더 | 내용 |
|---|---|
| `claim_extraction/` | claim 추출 모듈(음성·화면·정렬, 자체 conda env 2개). `extraction.py`가 백엔드에서 `main.py`를 실행해 결과를 run 폴더로 가져온다 |
| `claim_verification/` | `product_mapping/`(식약처 DB 매핑) → `verdict_b/`(NLI) → `verdict_a/`(규칙 판정 + 병합) → `explanation/`(설명문) |
| `scripts/` | `run_stage.py`·`run_all.py`(단계별·중간부터 실행), `import_enriched.py`(보강 sqlite → PostgreSQL 스키마 적재. `data/`의 덤프를 다시 만들 때) |

## 환경

`backend/setup.sh`가 만든다: conda env 3개(truead, truead-visual, truead-db) + `backend/requirements.txt`·추출 단계 requirements + llama.cpp 빌드 + GGUF 2종·HF 모델 + PostgreSQL(클러스터·DB·참조 DB 복원). 실행 방법은 `backend/README.md` 준비 절.

## 단계별 실행 (`backend/`에서)

```bash
python claim_process/scripts/run_stage.py {extraction|mapping|verdict_b|verdict_a} --input <경로> [--b-result <경로>] [--run-dir <경로>]
python claim_process/scripts/run_stage.py explanation --run-dir <run 폴더>             # 03·04가 있는 run 폴더의 04에 설명문 추가
python claim_process/scripts/run_all.py --from {claims|claims_with_db} <json>            # 기존 JSON에서 설명문까지
```

## 단계 산출물 (`runs/<UTC 시각>_<6자리>/`)

| 파일 | 내용 |
|---|---|
| `01_extraction/` | 추출 중간 JSON (`data/output/<영상>.*.json` 복사본) |
| `01_claims.json` | 추출 결과 (claims_all_db_matched_346 형식 + t_start/t_end) |
| `02_claims_with_db.json`, `02_product_mapping_audit.json`, `02_product_mapping_summary.json` | 제품 매핑 |
| `03_verdict_b.json`, `03_nli_results.json` | 판정 B (mechanism_b 형식, NLI 상세) |
| `04_final_results.json`, `04_final_summary.json` | 판정 A + 병합. 전체 실행(`main.py`·`run_all.py`)과 API 모두 `explanation` 단계에서 `explanation`을 넣는다 |
