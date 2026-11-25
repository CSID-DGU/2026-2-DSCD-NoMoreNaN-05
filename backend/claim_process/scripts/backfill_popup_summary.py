import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app import cache, llm
from claim_process.claim_extraction.common import LLMClient
from claim_process.claim_verification import explanation
from config import DB_VERSION

EXPLAINED = """db_version = %(v)s
  AND jsonb_typeof(result #> '{meta,db_version}') = 'array'
  AND result #>> '{meta,db_version,0}' = %(v)s
  AND jsonb_typeof(result #> '{results}') = 'array'
  AND NOT jsonb_path_exists(result, '$.results[*] ? (!(@.explanation.type() == "string" && @.explanation like_regex "\\\\S"))')"""
SUMMARIZED = """(jsonb_typeof(result #> '{videos,0,popup_summary}') = 'string'
  AND result #>> '{videos,0,popup_summary}' ~ '\\S')"""
UPDATE = "UPDATE results SET result = jsonb_set(result, '{videos,0,popup_summary}', to_jsonb(%s::text)) WHERE video_id = %s"


def count(where: str) -> int:
    return cache._con.execute(f"SELECT count(*) FROM results WHERE {where}", {"v": DB_VERSION}).fetchone()[0]


def main():
    cache.open()
    llm.start()
    try:
        llm.wait()
        missed = [r[0] for r in cache._con.execute(f"SELECT video_id FROM results WHERE ({EXPLAINED}) IS NOT TRUE",
                                                   {"v": DB_VERSION})]
        print("비적중:", " ".join(missed))
        targets = cache._con.execute(f"SELECT video_id, result FROM results WHERE {EXPLAINED} AND {SUMMARIZED} IS NOT TRUE",
                                     {"v": DB_VERSION}).fetchall()
        print(f"대상 {len(targets)}행", flush=True)
        client = LLMClient(explanation.LLM_BASE_URL, explanation.LLM_MODEL, explanation.TEMPERATURE,
                           explanation.REASONING_EFFORT, max_tokens=explanation.MAX_TOKENS, timeout=explanation.TIMEOUT)
        for video_id, result in targets:
            text = explanation.popup_summary(result["results"], client)
            cache._con.execute(UPDATE, (text, video_id))
            print(video_id, text, flush=True)
    finally:
        llm.stop()
    print(f"전체 {count('TRUE')}, 요약 있음 {count(SUMMARIZED)}, 새 HIT 조건 충족 {count(f'{EXPLAINED} AND {SUMMARIZED}')}, "
          f"비적중 {len(missed)}")
    cache.close()


if __name__ == "__main__":
    main()
