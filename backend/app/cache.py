import threading

import psycopg
from psycopg.types.json import Jsonb

from config import CACHE_DSN, DB_VERSION
from files import load_json, save_json

from . import jobs

DDL = """
CREATE TABLE IF NOT EXISTS results (
  video_id     text PRIMARY KEY,
  url          text NOT NULL,
  title        text,
  duration_sec double precision,
  db_version   text NOT NULL,
  job_id       text NOT NULL,
  cached_at    timestamptz NOT NULL,
  result       jsonb NOT NULL,
  video        bytea STORAGE EXTERNAL NOT NULL
)
"""
UPSERT = """
INSERT INTO results (video_id, url, title, duration_sec, db_version, job_id, cached_at, result, video)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (video_id) DO UPDATE SET url = excluded.url, title = excluded.title,
  duration_sec = excluded.duration_sec, db_version = excluded.db_version, job_id = excluded.job_id,
  cached_at = excluded.cached_at, result = excluded.result, video = excluded.video
"""
HIT = """
SELECT result, video FROM results WHERE video_id = %s AND db_version = %s
  AND jsonb_typeof(result #> '{meta,db_version}') = 'array'
  AND result #>> '{meta,db_version,0}' = %s
  AND jsonb_typeof(result #> '{results}') = 'array'
  AND NOT jsonb_path_exists(result, '$.results[*] ? (!(@.explanation.type() == "string" && @.explanation like_regex "\\\\S"))')
  AND jsonb_typeof(result #> '{videos,0,popup_summary}') = 'string'
  AND result #>> '{videos,0,popup_summary}' ~ '\\S'
"""

LOCK = threading.Lock()
_con: psycopg.Connection | None = None


def open() -> None:
    global _con
    close()
    _con = psycopg.connect(CACHE_DSN, autocommit=True)
    _con.execute(DDL)


def close() -> None:
    global _con
    if _con is not None:
        _con.close()
        _con = None


def restore_into(video_id: str, run_dir) -> bool:
    with LOCK:
        row = _con.execute(HIT, (video_id, DB_VERSION, DB_VERSION), binary=True).fetchone()
    if row is None:
        return False
    save_json(run_dir / "04_final_results.json", row[0])
    (run_dir / f"{video_id}.mp4").write_bytes(row[1])
    return True


def publish(job: dict) -> None:
    run_dir = jobs.RUNS_DIR / job["job_id"]
    video_id = job["video"]["video_id"]
    result = load_json(run_dir / "04_final_results.json")
    video = (run_dir / f"{video_id}.mp4").read_bytes()
    with LOCK:
        _con.execute(UPSERT, (video_id, job["url"], job["video"]["title"], job["video"]["duration_sec"],
                              DB_VERSION, job["job_id"], jobs.now(), Jsonb(result), video))
