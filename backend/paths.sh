# 공통 경로 기본값. 같은 이름의 환경변수로 덮어쓸 수 있다. setup.sh·start.sh·serve_*.sh가 source한다.
TRUEAD_PGDATA="${TRUEAD_PGDATA:-$HOME/truead_pgdata}"
TRUEAD_PG_PORT="${TRUEAD_PG_PORT:-15432}"   # config.py의 DSN 기본값과 같아야 한다. 바꾸면 TRUEAD_CACHE_DSN·TRUEAD_REF_DSN도 함께
TRUEAD_PG_LOG="${TRUEAD_PG_LOG:-$HOME/truead_postgres.log}"
TRUEAD_SERVER_LOG="${TRUEAD_SERVER_LOG:-$HOME/truead_server.log}"
LLAMA_DIR="${LLAMA_DIR:-$HOME/llama.cpp}"
LLAMA_SERVER="${LLAMA_SERVER:-$LLAMA_DIR/build/bin/llama-server}"
GGUF_ROOT="${GGUF_ROOT:-$HOME/hf_cache/gguf}"

conda_env_bin() {   # conda env 이름 → <prefix>/bin (conda run과 같은 이름 해석)
    local prefix
    prefix="$(conda run -n "$1" printenv CONDA_PREFIX)" || { echo "conda env 없음: $1  → bash setup.sh" >&2; return 1; }
    printf '%s/bin\n' "$prefix"
}
