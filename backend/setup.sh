#!/bin/bash
# 백엔드 전체 환경(API·검증·추출·DB)을 만든다. 이미 있는 것은 건너뛴다.
#   truead        API · 검증 · audio · alignment  (requirements.txt, audio/requirements.txt. qwen-asr가 transformers==4.57.6을 고정)
#   truead-visual visual                          (visual/requirements.txt. PaddleOCR-VL · V-JEPA 2가 transformers>=5 필요)
#   truead-db     PostgreSQL 18
# truead와 truead-visual을 나누는 이유: transformers 버전이 서로 맞지 않아 한 환경에 못 넣는다.
# 그 뒤 llama.cpp 빌드(없을 때), GGUF 2종(serve_llm.sh: gpt-oss-120b 63GB, serve_vlm.sh: Qwen3.5-122B 72GB), HF 모델 4종,
# PostgreSQL 클러스터·~/.pgpass·데이터베이스 2개·참조 DB 복원.
# 비밀번호: TRUEAD_PG_PASSWORD 환경변수, 없으면 프롬프트로 묻는다(필요할 때만). 위치는 paths.sh의 변수로 덮어쓴다.

set -e
cd "$(dirname "$0")"

need() {
    for c in "$@"; do
        command -v "$c" >/dev/null || { echo "필요한 명령 없음: $c (시스템에 설치 필요)" >&2; exit 1; }
    done
}

source paths.sh
need conda nvidia-smi git
[ -x "$LLAMA_SERVER" ] || need nvcc   # llama.cpp CUDA 빌드용 CUDA Toolkit
source "$(conda info --base)/etc/profile.d/conda.sh"

make_env() {
    if conda env list | grep -q "^$1 "; then
        echo "  $1 이미 존재 - 생성 스킵"
    else
        conda create -n "$@" -y
    fi
}

make_env truead python=3.12
conda activate truead
[ -x "$CONDA_PREFIX/bin/ffmpeg" ] || conda install -y -c conda-forge ffmpeg
pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu130
pip install -r claim_process/claim_extraction/audio/requirements.txt
pip install -r requirements.txt
pip check
python -c "import torch; print('[truead] torch', torch.__version__, 'cuda', torch.cuda.is_available())"
ffmpeg -version | head -1
conda deactivate

make_env truead-visual python=3.12
conda activate truead-visual
pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu130
pip install -r claim_process/claim_extraction/visual/requirements.txt
pip uninstall -y autoawq gptqmodel transnetv2-pytorch
pip check
python -c "import torch, transformers; print('[truead-visual] torch', torch.__version__, 'cuda', torch.cuda.is_available(), '| transformers', transformers.__version__)"

make_env truead-db -c conda-forge postgresql=18.6

if [ ! -x "$LLAMA_SERVER" ]; then
    if ! command -v cmake >/dev/null || ! command -v c++ >/dev/null; then
        conda install -y -c conda-forge cmake cxx-compiler
        conda deactivate
        conda activate truead-visual
    fi
    [ -d "$LLAMA_DIR" ] || git clone https://github.com/ggml-org/llama.cpp "$LLAMA_DIR"
    (cd "$LLAMA_DIR" && cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j 8)
    [ -x "$LLAMA_SERVER" ] || { echo "빌드 결과 $LLAMA_DIR/build/bin/llama-server 가 LLAMA_SERVER=$LLAMA_SERVER 와 다름. LLAMA_SERVER를 빌드 경로로 맞추거나 그 위치에 둔 뒤 다시 실행" >&2; exit 1; }
fi

if [ -f "$GGUF_ROOT/gpt-oss-120b-GGUF/UD-Q4_K_XL/gpt-oss-120b-UD-Q4_K_XL-00001-of-00002.gguf" ]; then
    echo "  gpt-oss-120b GGUF 있음 - 스킵"
else
    hf download unsloth/gpt-oss-120b-GGUF --include "UD-Q4_K_XL/*" \
        --local-dir "$GGUF_ROOT/gpt-oss-120b-GGUF"
fi
VLM_GGUF="$GGUF_ROOT/Qwen3.5-122B-A10B-GGUF"
if [ -f "$VLM_GGUF/UD-Q4_K_XL/Qwen3.5-122B-A10B-UD-Q4_K_XL-00001-of-00003.gguf" ] && [ -f "$VLM_GGUF/mmproj-F16.gguf" ]; then
    echo "  Qwen3.5-122B GGUF 있음 - 스킵"
else
    hf download unsloth/Qwen3.5-122B-A10B-GGUF --include "UD-Q4_K_XL/*" --include "mmproj-F16.gguf" \
        --local-dir "$VLM_GGUF"
fi
for m in Qwen/Qwen3-ASR-1.7B Qwen/Qwen3-ForcedAligner-0.6B PaddlePaddle/PaddleOCR-VL-1.6 Huffon/klue-roberta-base-nli; do
    hf download "$m"
done
conda deactivate

# ── PostgreSQL ────────────────────────────────────────
PG_BIN="$(conda_env_bin truead-db)"
CONN="host=127.0.0.1 port=$TRUEAD_PG_PORT user=truead_admin gssencmode=disable"
REF_DB=TrueAD_Evidence_Claim
REF_SCHEMA=claim_verification_enriched
REF_TABLES=(products ingredients diseases evidence claims claim_evidence_links dataset_registry)
REF_ROWS=(46846 1223 34861 3082 0 0 4)   # data/claim_verification_enriched.dump 기준. 덤프를 다시 만들면 함께 바꾼다
PASS_FILE="${PGPASSFILE:-$HOME/.pgpass}"
unset PGPASSWORD

PW=
get_password() {
    [ -n "$PW" ] && return
    if [ -n "$TRUEAD_PG_PASSWORD" ]; then
        PW="$TRUEAD_PG_PASSWORD"
    elif [ -t 0 ]; then
        read -rs -p "truead_admin 비밀번호: " PW
        echo
    else
        echo "TRUEAD_PG_PASSWORD가 없고 입력할 터미널도 없음" >&2
        exit 1
    fi
    [ -n "$PW" ] || { echo "빈 비밀번호는 쓸 수 없음" >&2; exit 1; }
    case "$PW" in *$'\n'*) echo "줄바꿈이 든 비밀번호는 쓸 수 없음" >&2; exit 1 ;; esac
}

q() { "$PG_BIN/psql" "$CONN dbname=$1" -w -tAc "$2"; }

pg_ok() {   # postgres와 이미 있는 대상 DB 모두에 .pgpass로 접속되는지
    local db
    q postgres "SELECT 1" >/dev/null 2>&1 || return 1
    for db in "$REF_DB" truead_cache; do
        [ -z "$(q postgres "SELECT 1 FROM pg_database WHERE datname='$db'")" ] || q "$db" "SELECT 1" >/dev/null 2>&1 || return 1
    done
}

pgpass_conflicts() {   # 호스트·포트·사용자·DB가 대상과 일치하는 줄 번호
    local n=0 line h p d u rest
    while IFS= read -r line || [ -n "$line" ]; do
        n=$((n + 1))
        [[ "$line" == \#* ]] && continue
        line=${line//\\\\/$'\x01'}
        line=${line//\\:/$'\x02'}
        IFS=: read -r h p d u rest <<<"$line"
        [[ "$h" == 127.0.0.1 || "$h" == "*" ]] || continue
        [[ "$p" == "$TRUEAD_PG_PORT" || "$p" == "*" ]] || continue
        [[ "$d" == postgres || "$d" == "$REF_DB" || "$d" == truead_cache || "$d" == "*" ]] || continue
        [[ "$u" == truead_admin || "$u" == "*" ]] || continue
        echo "$n"
    done <"$PASS_FILE"
}

ref_diff() {   # 참조 스키마의 표·행 수가 기대값과 다른 부분
    local i t n out=""
    for i in "${!REF_TABLES[@]}"; do
        t=${REF_TABLES[$i]}
        if [ -z "$(q "$REF_DB" "SELECT 1 FROM information_schema.tables WHERE table_schema='$REF_SCHEMA' AND table_name='$t'")" ]; then
            out+=" $t:없음"
            continue
        fi
        n=$(q "$REF_DB" "SELECT count(*) FROM $REF_SCHEMA.$t")
        [ "$n" = "${REF_ROWS[$i]}" ] || out+=" $t:${n}행(기대 ${REF_ROWS[$i]})"
    done
    printf '%s' "$out"
}

if [ -f "$TRUEAD_PGDATA/PG_VERSION" ]; then
    echo "  클러스터 $TRUEAD_PGDATA 이미 존재 - initdb 스킵"
else
    get_password
    pwfile="$(umask 077; mktemp)"
    trap 'rm -f "$pwfile"' EXIT
    printf '%s\n' "$PW" >"$pwfile"
    "$PG_BIN/initdb" -D "$TRUEAD_PGDATA" -U truead_admin --encoding=UTF8 --locale=C.UTF-8 \
        --auth-local=scram-sha-256 --auth-host=scram-sha-256 --pwfile="$pwfile"
    rm -f "$pwfile"
fi

rc=0; "$PG_BIN/pg_ctl" -D "$TRUEAD_PGDATA" status >/dev/null 2>&1 || rc=$?
case $rc in
  0) port=$(sed -n 4p "$TRUEAD_PGDATA/postmaster.pid")
     [ "$port" = "$TRUEAD_PG_PORT" ] || { echo "$TRUEAD_PGDATA 는 포트 $port 로 실행 중 (TRUEAD_PG_PORT=$TRUEAD_PG_PORT)" >&2; exit 1; }
     echo "  PostgreSQL 이미 실행 중 - 기동 스킵" ;;
  3) "$PG_BIN/pg_ctl" -D "$TRUEAD_PGDATA" -l "$TRUEAD_PG_LOG" -o "-h 127.0.0.1 -p $TRUEAD_PG_PORT -k \"$HOME\"" -w start ;;
  *) echo "pg_ctl status returned $rc (see $TRUEAD_PG_LOG)" >&2; exit "$rc" ;;
esac

if pg_ok; then
    echo "  $PASS_FILE 로 접속됨 - 비밀번호 줄 추가 스킵"
else
    get_password
    PGPASSWORD="$PW" q postgres "SELECT 1" >/dev/null || { echo "비밀번호 불일치: $PASS_FILE 은 바꾸지 않았음" >&2; exit 1; }
    if [ -e "$PASS_FILE" ]; then
        mode=$(stat -c %a "$PASS_FILE")
        [ "$mode" = 600 ] || [ "$mode" = 400 ] || { echo "$PASS_FILE 권한이 $mode (0600 또는 0400이어야 libpq가 읽는다). chmod 0600 뒤 다시 실행" >&2; exit 1; }
        lines=$(pgpass_conflicts | tr '\n' ' ')
        [ -z "$lines" ] || { echo "$PASS_FILE ${lines}번째 줄이 127.0.0.1:$TRUEAD_PG_PORT truead_admin과 겹치지만 postgres·$REF_DB·truead_cache 모두에 접속되지는 않음. 그 줄을 고치거나(데이터베이스 '*', 올바른 비밀번호) 지운 뒤 다시 실행" >&2; exit 1; }
        [ -w "$PASS_FILE" ] || { echo "$PASS_FILE 에 쓸 수 없음(권한 $mode). 127.0.0.1:$TRUEAD_PG_PORT:*:truead_admin:<비밀번호> 줄을 직접 추가" >&2; exit 1; }
        [ ! -s "$PASS_FILE" ] || [ -z "$(tail -c1 "$PASS_FILE")" ] || echo >>"$PASS_FILE"
    else
        (umask 077; mkdir -p "$(dirname "$PASS_FILE")")
    fi
    esc=${PW//\\/\\\\}
    esc=${esc//:/\\:}
    (umask 077; printf '127.0.0.1:%s:*:truead_admin:%s\n' "$TRUEAD_PG_PORT" "$esc" >>"$PASS_FILE")
    pg_ok || { echo "$PASS_FILE 에 줄을 추가했지만 접속되지 않음" >&2; exit 1; }
    echo "  $PASS_FILE 에 127.0.0.1:$TRUEAD_PG_PORT:*:truead_admin 줄 추가"
fi

for db in "$REF_DB" truead_cache; do
    if [ -n "$(q postgres "SELECT 1 FROM pg_database WHERE datname='$db'")" ]; then
        echo "  데이터베이스 $db 이미 존재 - 스킵"
    else
        "$PG_BIN/createdb" --maintenance-db="$CONN dbname=postgres" -w "$db"
    fi
done

if [ -z "$(q "$REF_DB" "SELECT 1 FROM pg_namespace WHERE nspname='$REF_SCHEMA'")" ]; then
    "$PG_BIN/pg_restore" --dbname="$CONN dbname=$REF_DB" \
        --single-transaction --no-owner --no-privileges --no-password \
        data/claim_verification_enriched.dump
    diff=$(ref_diff)
    [ -z "$diff" ] || { echo "복원 뒤 참조 스키마가 기대와 다름:$diff" >&2; exit 1; }
    echo "  참조 스키마 $REF_SCHEMA 복원 완료"
else
    diff=$(ref_diff)
    [ -z "$diff" ] || { echo "스키마 $REF_SCHEMA 가 불완전함:$diff. 직접 확인 후 DROP SCHEMA $REF_SCHEMA CASCADE 로 지우고 다시 실행" >&2; exit 1; }
    echo "  참조 스키마 $REF_SCHEMA 이미 복원됨 - 스킵"
fi

echo
echo "conda env: $(conda_env_bin truead) $(conda_env_bin truead-visual) $PG_BIN"
echo "llama-server: $LLAMA_SERVER"
echo "GGUF: $GGUF_ROOT"
echo "PostgreSQL: $TRUEAD_PGDATA (127.0.0.1:$TRUEAD_PG_PORT, 접속 확인됨)"
