#!/usr/bin/env bash
set -e
source "$(dirname "$0")/paths.sh"
export PYTHONUNBUFFERED=1
exec > >(tee -a -i "$TRUEAD_SERVER_LOG") 2>&1
PG_CTL="${TRUEAD_PG_CTL:-$(conda_env_bin truead-db)/pg_ctl}"
rc=0; "$PG_CTL" -D "$TRUEAD_PGDATA" status >/dev/null 2>&1 || rc=$?
case $rc in
  0) ;;
  3) "$PG_CTL" -D "$TRUEAD_PGDATA" -l "$TRUEAD_PG_LOG" -o "-h 127.0.0.1 -p $TRUEAD_PG_PORT -k '"$HOME"'" -w start ;;
  *) echo "pg_ctl status returned $rc (see $TRUEAD_PG_LOG)"; exit "$rc" ;;
esac
exec uvicorn app.main:app --host 0.0.0.0 --port 5000
