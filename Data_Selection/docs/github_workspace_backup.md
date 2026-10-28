# GitHub 작업 기록 및 DB 백업

저장소: CSID-DGU/2026-2-DSCD-NoMoreNaN-05, 브랜치: data-selection, 프로젝트 폴더: Data_Selection.

코드·설정 템플릿·문서는 Data_Selection에서 바로 열 수 있음. 수집 원문·매핑 중간 결과·검토용 JSON·최종 전달 JSON·SQLite·PostgreSQL 백업은 workspace_snapshots 아래의 전체 작업 스냅샷에 포함함. 대용량 스냅샷은 40MiB 이하 파트로 나누고 manifest.json에 파일별/파트별 SHA256을 기록함.

`.env`, API 키/비밀번호, 가상환경, 다운로드한 모델·도구, 캐시 바이트코드와 실행 잠금 파일은 제외함. 저장된 HTTP URL에 API 키가 있으면 업로드 사본에서 제거함. 원본 파일은 수정하지 않음. 권한 문제로 읽을 수 없는 파일은 manifest.excluded_unreadable에 명시함.

기본 스냅샷에서 읽기 제한으로 제외됐던 `text_test_data/images`의 이미지 1,066개는 별도 읽기 권한으로 `workspace_snapshots/images_<timestamp>/` 보충 스냅샷에 포함함. 기본 스냅샷의 제외 표시는 이 보충본으로 해결됨.

## 복원

GitHub에서 data-selection 브랜치를 clone한 뒤 Data_Selection으로 이동함. Python 표준 라이브러리만으로 스냅샷을 복원할 수 있음.

```bash
python scripts/restore_workspace_snapshot.py workspace_snapshots/<snapshot-directory> --destination ../TRUEAD_restored
```

대상 디렉터리는 비어 있어야 함. 파트/ZIP/각 파일의 해시를 확인한 뒤 복원함. `Data_List_Claim_Verification/*.sqlite`는 SQLite 도구로 열 수 있음. `exports/postgres_snapshot_20261028/truead.dump`는 2026-10-28 현재 로컬 PostgreSQL의 custom-format 백업임. PostgreSQL/pgvector를 별도 설치한 후 빈 DB로 복원함.

이미지 보충본은 같은 명령으로 별도 빈 폴더에 복원한 뒤, 그 안의 `text_test_data/images` 폴더를 기본 복원본의 `text_test_data/` 아래에 복사하면 됨.

```bash
pg_restore --no-owner --no-acl --dbname <empty_database> exports/postgres_snapshot_20261028/truead.dump
```

실행 환경은 requirements*.txt로 새로 설치하고 `.env.example`을 참고하여 개인 환경변수와 키를 설정함. 복원된 실행 상태 파일이나 저장된 PID는 과거 기록이므로 실행 중임을 의미하지 않음. 추론/수집 작업은 자동으로 재시작하지 않음.

## 현재 결과

- 제품명 후보 검색: 289개 제품 항목 중 262개(90.7%).
- 제조사로 복수 후보 구분 후 단일 제품 선택: 238개(82.4%). 정답 정확도와 다름.
- 전달 JSON: data/processed/product_functionality_handoff/mapped_products.json. 제품 238개, Claim 2,912개. 원본 URL/Claim과 DB main_functionality를 함께 보존함.
- 원료 근거 검색은 같은 제품 Claim의 명시적인 긍정 함유/사용 주장에 한정함. 단순 효능 언급이나 제품 식별 실패를 이유로 자동 원료 검색하지 않음.
- 이전 전체 BGE 재순위 작업은 사용자 요청으로 중단된 기록이며 자동 재개하지 않음. 저장된 점수/중간 결과는 스냅샷에 보존함.

업로드 전 전체 테스트 및 자격 증명 검사를 수행함. 스냅샷은 GitHub 파일 제한을 피하기 위한 데이터 보관 방식이며 자동 배포나 서비스 실행은 수행하지 않음.

게시 전 회귀 테스트 93개와 ZIP/파트 무결성 검사 통과함.
