# TRUEAD Backend Pipeline

| 폴더 | 내용 |
|---|---|
| `claim_process/` | claim 추출 → 검증 파이프라인(`claim_extraction/`, `claim_verification/`, `scripts/`). 단계·산출물·단계별 실행은 `claim_process/README.md` |
| `app/` | FastAPI API·작업 큐·결과 캐시 |
| `data/` | `manufacturer_pairs.json`, 참조 DB 덤프 `claim_verification_enriched.dump` |
| `tests/` | 로컬 테스트 (`pytest -q -m "not gpu"`) |

## 실행

```bash
python main.py <영상.mp4> [--url URL] [--title TITLE] [--b-source TEXT]     # 영상 1편 전체
./start.sh                                                               # API 서버: PostgreSQL 확인·기동 후 uvicorn :5000(외부 210.94.179.19:9326) + gpt-oss llama-server :8000 (8002는 VLM, --workers 쓰지 않음)
```

실행마다 `runs/<UTC 시각>_<6자리>/`에 단계별 결과를 저장한다(파일 목록은 `claim_process/README.md`).

`./start.sh`의 화면 출력은 `~/truead_server.log`에도 이어서 저장된다.

API 워커는 판정 병합 뒤 `explanation` 단계에서 gpt-oss-120b(llama-server :8000)로 claim 행·`A.checks[]`·`B`마다 설명문 `explanation`을 만들어 `04_final_results.json`에 넣는다. 실패하면 `VERIFY_FAILED`. `python main.py`·`claim_process/scripts/run_all.py`도 같은 단계를 거친다. 실패하면 오류로 끝나고 04는 설명문 없이 남는다.

8000번 llama-server는 API가 기동할 때 여유 메모리가 가장 큰 GPU 한 장에 띄워 두고(이미 떠 있으면 그대로 쓰고 내리지 않음) 종료할 때 내린다. 여유 24GB 카드가 없으면 API는 기동하지 않는다. 추출·설명 단계는 이 서버를 같이 쓴다(카드 번호는 `SERVER_GPUS`로 추출 subprocess에 넘어가 그 카드를 피한다). 작업을 시작하기 전에 서버가 죽어 있으면 다시 띄운다(적재 중이면 준비될 때까지 기다린다). 미리 띄운 서버를 쓰게 하려면 `GPUS=<n> bash claim_process/claim_extraction/serve_llm.sh` 뒤 `SERVER_GPUS=<n> ./start.sh`. 8000번 서버는 반드시 이 스크립트로 띄운 것이어야 한다(모델 별칭 `gpt-oss-120b`·슬롯 4·컨텍스트 32768 전제, 재사용 시 확인하지 않음). VLM(:8002)은 작업마다 띄우고 내린다.

종료: Ctrl-C 1회 또는 `kill <pid>`(`start.sh`의 PID = uvicorn PID, SIGINT·SIGTERM): 진행 중 작업을 끝낸 뒤 API가 띄운 llama-server를 내리고 종료한다. 대기 중(QUEUED)이던 작업은 다음 기동 때 실패로 바뀐다. Ctrl-C를 더 누르면 결과를 보장하지 않는다(시점에 따라 바로 끝나며 추출 subprocess·llama-server가 남을 수 있음) — `nvidia-smi`·`pgrep -f 'claim_extraction/main.py|llama-server'`로 확인해 내린다. 남은 llama-server를 재사용하려면 `SERVER_GPUS=<n> ./start.sh`.

## 준비 (1회)

전제(시스템에 이미 있어야 함. sudo가 필요하면 관리자에게): NVIDIA 드라이버·`nvidia-smi`, CUDA Toolkit의 `nvcc`(llama.cpp CUDA 빌드용, 드라이버에는 들어 있지 않음), conda(miniforge·anaconda 무관), git, 디스크 150GB 이상(GGUF 63GB + 72GB), 네트워크. `cmake`·C++ 컴파일러가 없으면 `setup.sh`가 conda(`truead-visual`)에 설치한다. GPU는 최소 3장: 상주 LLM(여유 24GB 이상) 1장, 작업 중 VLM(18GB 이상) 1장, keyframe·audio(각 8GB 이상) 1장 — 서버 카드는 다른 단계가 피한다. 두 서버는 전문가 층 일부를 CPU 메모리에 두므로 RAM도 넉넉해야 한다(503GB 서버에서 확인). 처음 실행은 GGUF 다운로드와 llama.cpp 빌드로 오래 걸린다.

```bash
git clone <repo> && cd <repo>/backend
TRUEAD_PG_PASSWORD=<새 DB 비밀번호> bash setup.sh   # 환경변수를 생략하면 필요할 때 프롬프트로 묻는다
conda activate truead && ./start.sh
```

`setup.sh`가 하는 일(이미 있으면 건너뜀): conda env `truead`(API·검증·음성·정렬)·`truead-visual`(화면)·`truead-db`(PostgreSQL 18), `requirements.txt`, `~/llama.cpp` CUDA 빌드, GGUF 2종(`~/hf_cache/gguf/`), HF 모델 4종(기본 캐시), PostgreSQL 클러스터 `~/truead_pgdata`(사용자 `truead_admin`, 127.0.0.1:15432) 생성·기동, `~/.pgpass` 1줄(`127.0.0.1:15432:*:truead_admin:<비밀번호>`, 0600), 데이터베이스 `TrueAD_Evidence_Claim`·`truead_cache`, 참조 DB 스키마 `claim_verification_enriched` 복원(`data/claim_verification_enriched.dump`, products 46846). `~/.pgpass`에 같은 호스트·포트·사용자의 틀린 줄이 있거나 권한이 0600·0400이 아니면 파일을 고치지 않고 멈춘다. 스키마가 이미 있는데 표·행 수가 덤프와 다르면 지우지 않고 멈춘다(다시 하려면 `DROP SCHEMA claim_verification_enriched CASCADE`를 직접 실행).

위치를 바꾸려면 `paths.sh`의 변수를 환경변수로 덮어쓴다: `TRUEAD_PGDATA`, `TRUEAD_PG_LOG`, `TRUEAD_SERVER_LOG`, `LLAMA_DIR`, `LLAMA_SERVER`, `GGUF_ROOT`, `TRUEAD_PG_CTL`(start.sh), `PGPASSFILE`(`.pgpass` 위치). `setup.sh` 때 지정한 환경변수는 `start.sh`(와 `serve_*.sh`)를 실행할 때도 같이 줘야 한다. `TRUEAD_PG_PORT`를 15432에서 바꾸면 `TRUEAD_CACHE_DSN`·`TRUEAD_REF_DSN`도 같은 포트로 넘긴다. 참조 DB 접속 문자열을 바꾸려면 `TRUEAD_REF_DSN="host=… port=… dbname=… user=… gssencmode=disable options='-c search_path=claim_verification_enriched'"` (`options=…`를 빼면 서버 기본 검색 경로의 표를 읽는다).

수동 복원(`backend/`에서. `pg_restore`는 반드시 `truead-db` env의 것(PostgreSQL 18)을 쓴다):
```bash
conda run -n truead-db pg_restore \
  --dbname="host=127.0.0.1 port=15432 dbname=TrueAD_Evidence_Claim user=truead_admin gssencmode=disable" \
  --single-transaction --no-owner --no-privileges --no-password \
  data/claim_verification_enriched.dump
conda run -n truead-db psql \
  "host=127.0.0.1 port=15432 dbname=TrueAD_Evidence_Claim user=truead_admin gssencmode=disable" \
  -c "SELECT count(*) FROM claim_verification_enriched.products"      # 46846
```

덤프 다시 만들기(보강 sqlite가 바뀌었을 때): `python claim_process/scripts/import_enriched.py --source <sqlite> --dsn "host=127.0.0.1 port=15432 dbname=TrueAD_Evidence_Claim user=truead_admin gssencmode=disable"`로 적재한 뒤
`conda run -n truead-db pg_dump --dbname="host=127.0.0.1 port=15432 dbname=TrueAD_Evidence_Claim user=truead_admin gssencmode=disable" --schema=claim_verification_enriched --format=custom --no-privileges --no-password --file=data/claim_verification_enriched.dump`. 표별 행 수가 바뀌면 `setup.sh`의 `REF_ROWS`도 함께 고친다.

## 결과 캐시 (PostgreSQL)

같은 영상의 결과·mp4는 기존 클러스터 `~/truead_pgdata`(127.0.0.1:15432)의 데이터베이스 `truead_cache`, 테이블 `results`에 저장한다. 테이블은 API가 기동할 때 만든다. PostgreSQL에 붙지 못하면 API는 기동하지 않는다. 큐에서 기다리던 작업도 차례가 왔을 때 캐시를 다시 확인하므로, 같은 영상이 겹쳐 들어오면 앞 작업의 게시가 성공한 경우 뒤 작업은 처리 없이 완료되며 상태 조회에서는 30초(단계별 5·10·15초)에 걸쳐 단계가 넘어간 뒤 DONE으로 보인다. 적중 여부는 `job.json`의 `cached`에만 남고 API 응답에는 드러나지 않는다.

1. 기동은 `./start.sh`가 대신한다(꺼져 있으면 아래 명령으로 띄우고, 켜져 있으면 그대로 진행). 백엔드를 내려도 PostgreSQL은 내리지 않는다. 손으로 띄우려면:
   `conda activate truead-db && pg_ctl -D ~/truead_pgdata -l ~/truead_postgres.log -o "-h 127.0.0.1 -p 15432 -k $HOME" -w start`
2. 데이터베이스·`.pgpass`는 `setup.sh`가 만든다. 손으로 만들려면:
   `conda run -n truead-db createdb --maintenance-db="host=127.0.0.1 port=15432 user=truead_admin dbname=postgres gssencmode=disable" -w truead_cache`
3. 비밀번호는 코드·레포에 넣지 않는다. `setup.sh`가 `~/.pgpass`에 쓴 한 줄(데이터베이스 `*`)을 두 데이터베이스가 함께 쓴다.
4. 접속 문자열을 바꾸려면 `TRUEAD_CACHE_DSN="host=… port=… dbname=… user=… gssencmode=disable"`.
   CORS 허용 origin을 바꾸려면 `TRUEAD_CORS_ORIGINS="http://a.test,http://b.test"`(쉼표 구분, 기본 `http://210.94.179.19:9332,http://210.94.179.19:9321,http://localhost:5173`).
5. API: `conda activate truead && cd backend && ./start.sh`. 실행 중 DB 연결이 끊기면 재연결하지 않으므로 `./start.sh`를 다시 실행한다.
