# 서버에서 기존 작업과 분리하여 사용하기

저장소: https://github.com/CSID-DGU/2026-2-DSCD-NoMoreNaN-05
브랜치: `data-selection`. 이 문서와 코드는 `Data_Selection` 아래에 있음.

## 권장 배치

```text
~/truead/
  checkouts/data-selection/    # Git 체크아웃, pull 전용
  runs/20261103/              # 이번 작업의 복원본, DB·CSV·JSON·실행 코드
```

기존 `/home/yongbin53/DataScience-Capstone/No-More-NaN-shared`는 그대로 둠.
공유 DB에 덮어쓰거나 그 폴더에서 git pull하지 않고 본인 홈에 별도 체크아웃을 생성함.
Git 체크아웃과 실행 폴더를 나누므로 이후 pull이 실행 중인 코드나 DB를 변경하지 않음.

## 처음 받을 때 (서버 Bash 터미널)

```bash
mkdir -p ~/truead/checkouts ~/truead/runs
git clone --branch data-selection --single-branch https://github.com/CSID-DGU/2026-2-DSCD-NoMoreNaN-05.git ~/truead/checkouts/data-selection
cd ~/truead/checkouts/data-selection/Data_Selection
conda create -n truead-20261103 python=3.12 -y
conda activate truead-20261103
python -m pip install -r requirements.txt

# images_ 보충본을 제외한 최신 전체 스냅샷 선택
snapshot=$(python -c "from pathlib import Path; print(sorted(p.parent for p in Path('workspace_snapshots').glob('*/manifest.json') if not p.parent.name.startswith('images_'))[-1])")
python scripts/restore_workspace_snapshot.py "$snapshot" --destination ~/truead/runs/20261103
cd ~/truead/runs/20261103
```

복원 대상은 비어 있어야 함. 기존 경로가 사용 중이면 날짜/번호가 다른 새 폴더를 지정함.
이후 사용할 코드와 자료는 `runs/20261103` 안의 파일임.
API 키와 비밀번호는 제외했으므로 필요할 때 서버에 `.env`를 별도로 설정함.
원래 API 수집·모델 평가·DB 보강 명령은 자동 실행하지 않음.
임베딩·reranker를 실행할 때만 별도 requirements 파일로 모델 의존성을 설치함.

## 보강 DB 확인

```bash
python -c "import sqlite3; from pathlib import Path; p=Path('TRUEAD_DB_보강자료/claim_verification.sqlite').resolve(); c=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True); print(c.execute('SELECT COUNT(*) FROM products').fetchone()[0]); c.close()"
```

예상 제품 수는 **46,846건**임. 원본의 빈칸 3건을 보충하고 신규 제품 681건과 보강 컬럼 20개를 추가한 DB임.
`scripts/inspect_md_enrichment_sources.py`는 작업 폴더의 `TRUEAD_DB_보강자료`를 우선 사용하며,
다른 위치를 쓸 때는 `TRUEAD_ENRICHMENT_DIR` 환경변수로 지정할 수 있음.
이미 보강된 DB에 `enrich_db_from_md.py --apply`를 다시 실행할 필요 없음.
과거 실행 로그·일부 스크립트에는 Windows 경로가 남아 있으므로 실행 인자와 파일 위치를 확인함.

## 전달 파일과 현재 제한

- `exports/claim_type_db_20261103/claims_with_db.json`: 535개 영상, 8,728개 Claim. 원본 `effect` 보존.
- `data/processed/claim_json_feedback_audit/`: 전달본 피드백의 읽기 전용 점검 결과.
- 보강 원본 CSV·MD 및 DB: `TRUEAD_DB_보강자료/`.
- 전체 복원본에는 기존 DB 및 과거 결과도 들어 있으므로 최신 보강 DB 경로를 명시해서 사용함.
- 전달 JSON은 판정 완료본이 아님. 브랜드를 업체명과 비교해 제조사 충돌을 놓친 confirmed 9건,
  제조사 미확인 confirmed, 후보 수 표현 불일치, 원료 분류 일부 과다 연결이 확인되었으며 아직 수정 전임.
- `product_ref`로 같은 영상 제품을 참조하지 못하는 Claim 290개가 있음. 다른 제품 DB를 대신 사용하면 안 됨.
- 브랜드만 있으면 브랜드 비교, 제조사만 있으면 제조사 비교, 둘 다 있으면 제조사 우선이라는 새 합의는
  기존 전달본 전체에 아직 반영되지 않았음. 매핑률은 정답 검증에 따른 정확도와 다름.
- 실행 환경/모델 다운로드/비밀키 및 접근 불가한 `text_test_data/images`는 이번 스냅샷에서 제외함.
  과거 이미지 보충 스냅샷은 저장소에 별도 보존됨.

## 이후 코드 갱신

```bash
cd ~/truead/checkouts/data-selection
git pull --ff-only origin data-selection
```

새 스냅샷은 다른 실행 폴더에 복원하고 점검 후 사용함. 기존 실행 DB는 자동으로 바뀌지 않음.
각 스냅샷의 `manifest.json`에는 포함 파일과 해시, 분할 파일 해시, 제외 항목이 기록되어 있으며
복원 스크립트가 이를 확인함.
