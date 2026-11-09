# 2026-11-09 코드 업데이트

브랜치: `data-selection`, 프로젝트 경로: `Data_Selection/`.

이번 업데이트는 코드와 Markdown 작업 문서를 보존함. JSON/JSONL, SQLite/PostgreSQL 데이터, 압축 백업, 실행 상태, 실제 `.env`는 새로 올리거나 갱신하지 않음. 과거 커밋에 이미 있던 JSON과 백업은 삭제하지 않음. `.gitignore`는 이미 추적 중인 파일을 제거하지 않으므로, 이번 커밋에 데이터 변경이 없는지도 따로 확인함.

## 제품 재매핑

`scripts/remap_product_input.py`는 새 입력을 보강 SQLite DB에서 다시 검색함. `--threshold`로 편집 거리 기반 후보 검색 점수를 지정하며 기본값은 70임. 80점 결과는 다음 명령으로 재현함.

```bash
python scripts/remap_product_input.py \
  --input /path/to/claims_matched_346_not_matched_40.json \
  --database /path/to/claim_verification.sqlite \
  --threshold 80 \
  --output-dir /path/to/results_t80
```

입력 영상 386개, 제품 항목 709개 기준 80점 실행 결과는 후보 검색 695개, 기존 확정 조건 통과 671개(94.64%)임. 제품명·브랜드 중복 제거 기준은 284개 중 261개(91.90%)임. 연결률이며 제품 동일성의 수동 정답 대조 정확도는 아님.

제조사 정리, 승인 제조사 PAIR, 같은 제품 Claim의 명시적 제조사 및 브랜드 보조 비교와 신고번호 보조 검색을 적용함. `confirmed / unresolved / not_found`를 유지하고, 타입별 DB 객체는 confirmed에만 채움. 원본 Claim과 effect 및 claim_type 배열을 보존함. 입력과 DB는 읽기 전용으로 사용함.

## 평가 데이터 관련 코드

- `scripts/build_synthetic_video_eval_100.py`: 제품 1개 영상 90개와 2개 영상 10개의 평가 묶음 생성.
- `scripts/label_eval100_all_claims.py`: 검토해 저장한 결정으로 정답 파일을 구성함. 새로운 입력을 자동으로 정답 판정하는 모델이 아님.
- `scripts/export_restored_claim_handoff.py`: 합의된 전달 형식 복구 및 제품 확인 조건 적용.
- `scripts/export_candidate_db_handoff.py`: 과거 후보 전달 실험 기록임. 현재 팀 전달 형식으로 지정하지 않음.

기존 Claim 1,424개와 합성 Claim 130개의 평가 정답 작업 문서는 exports 아래 Markdown에 보존함. 실제 입력·정답 JSON은 이번 업로드 대상이 아님.

## 별도로 필요한 로컬 자료

새 서버에서 코드를 받는 것만으로 데이터 작업 전체를 실행할 수 있는 것은 아님. 원본 입력 JSON, 보강 DB, 승인 제조사 PAIR 설정, 작업별 검토 결정 및 원본 데이터가 필요함. 이번에는 JSON을 업로드하지 않으므로 아래 새 검토 설정도 로컬에서 별도로 준비해야 함.

- `configs/eval100_manual_review_20261105.json`
- `configs/eval100_review_batch5_20261105.json`
- `configs/eval100_review_batch6_20261105.json`
- `configs/eval100_review_final_overrides_20261105.json`

후속 요청에 따라 브랜치에서 JSON/JSONL 추적 파일을 모두 제거함. `configs/manufacturer_pairs.json`도 로컬에서 별도로 준비해야 함. requirements 파일로 환경을 설치하고, 실제 인증 값은 개인 `.env` 또는 환경변수로 설정함.

## JSON 제거 후속 작업

최신 브랜치에서는 JSON/JSONL 파일을 추적하지 않음. 로컬 원본과 업로드용 폴더의 파일은 보존하고 Git 추적만 해제함. 과거 커밋과 기존 ZIP·분할 ZIP 백업은 그대로이므로, 이 작업은 민감정보의 이력 완전 삭제가 아님. 백업 manifest JSON 역시 별도 준비가 필요함. 저장소의 과거 백업 복원 설명은 당시 manifest가 있을 때의 절차임.

로컬 단위 테스트 171개가 통과했으며 Mechanism A/B 실제 수신 코드 실행은 별도로 검증하지 않음.
