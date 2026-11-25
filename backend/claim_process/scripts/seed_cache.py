import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse
import subprocess
import time
import traceback
from urllib.parse import parse_qs, urlsplit

from psycopg.types.json import Jsonb

from app import cache, jobs, llm, video, worker
from claim_process.claim_verification import adapters, explanation, verdict_a, verdict_b
from config import BACKEND_DIR, DB_VERSION
from files import load_json, save_json

ROOT = BACKEND_DIR.parents[1]
JSON_DIR = ROOT / "JSON"
VIDEO_DIR = ROOT / "youtube_video"
WORK_DIR = ROOT / "backend_docs" / "cache_seed"
CLAIMS_PATH = JSON_DIR / "(이정님 파트)claims_with_db_test.json"
FINAL_PATH = JSON_DIR / "(시은 파트)final_results.json"
TITLE_PATHS = [JSON_DIR / "claims_matched_346_not_matched_40.json", JSON_DIR / "claims_all_db_matched_346.json"]

INSERT = """
INSERT INTO results (video_id, url, title, duration_sec, db_version, job_id, cached_at, result, video)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (video_id) DO NOTHING
"""


def hit(ytid: str) -> bool:
    return cache._con.execute(cache.HIT, (ytid, DB_VERSION, DB_VERSION)).fetchone() is not None


def exists(ytid: str) -> bool:
    return cache._con.execute("SELECT 1 FROM results WHERE video_id = %s", (ytid,)).fetchone() is not None


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def label_diff(result: dict, expected: list[dict]) -> dict:
    mine = {(r["product_ref"], r["claim_id"]): r for r in result["results"]}
    diff = {"rows": len(result["results"]), "expected_rows": len(expected), "missing": 0,
            "A": 0, "B": 0, "final": 0, "any": 0}
    for e in expected:
        r = mine.get((e["product_ref"], e["claim_id"]))
        if r is None:
            diff["missing"] += 1
            continue
        a = [(x or {}).get("label") for x in (r["A"], e["A"])]
        b = [(x or {}).get("label") for x in (r["B"], e["B"])]
        d = {"A": a[0] != a[1], "B": b[0] != b[1], "final": r["final_label"] != e["final_label"]}
        for k, v in d.items():
            diff[k] += v
        diff["any"] += any(d.values())
    return diff


def seed(item: dict, ytid: str, title: str | None, expected: list[dict]) -> dict:
    url = item["url"]
    if exists(ytid):
        return {"status": "exists" if hit(ytid) else "existing-miss"}
    if not item["claims"] or worker.mapping_all_failed([item]):
        return {"status": "skip", "reason": "mapping"}
    run_dir = WORK_DIR / "runs" / ytid
    run_dir.mkdir(parents=True, exist_ok=True)
    mp4 = VIDEO_DIR / f"{item['video_id']}.mp4"
    try:
        if title is None:
            _, title, _ = video.probe(url)
        if not mp4.exists():
            mp4 = video.download(url, run_dir, ytid)
    except Exception as e:
        return {"status": "skip", "reason": f"fetch: {e!r}"}
    v = {**item, "video_id": ytid, "title": title}
    input_path = run_dir / "02_claims_with_db.json"
    save_json(input_path, [v])
    b = verdict_b.run([v], run_dir)
    verdict_a.run([v], adapters.b_records(b), run_dir, input_path=input_path, b_path=run_dir / "03_verdict_b.json")
    llm.wait()
    explanation.run(run_dir)
    result = load_json(run_dir / "04_final_results.json")
    ok = result["meta"]["db_version"][:1] == [DB_VERSION] and all(
        isinstance(r.get("explanation"), str) and r["explanation"].strip() for r in result["results"])
    if not ok:
        return {"status": "skip", "reason": "verify"}
    cache._con.execute(INSERT, (ytid, url, title, duration(mp4), DB_VERSION, f"seed-{ytid}", jobs.now(),
                                Jsonb(result), mp4.read_bytes()))
    return {"status": "ok", "labels": label_diff(result, expected)}


def main():
    parser = argparse.ArgumentParser(description="평가 영상 결과를 캐시 DB에 미리 채운다")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    expected = {}
    for r in load_json(FINAL_PATH)["results"]:
        expected.setdefault(r["video_id"], []).append(r)
    items = [v for v in load_json(CLAIMS_PATH) if v["video_id"] in expected][:args.limit]
    titles = {}
    for p in TITLE_PATHS:
        titles.update({v["url"]: v["title"] for v in load_json(p) if v.get("title")})

    report_path = WORK_DIR / "report.json"
    report = load_json(report_path) if report_path.exists() else {}
    cache.open()
    llm.start()
    try:
        for item in items:
            ytid = parse_qs(urlsplit(item["url"]).query)["v"][0]
            t0 = time.time()
            if item["video_id"].split("_", 2)[2] != ytid:
                out = {"status": "skip", "reason": "id-mismatch"}
            else:
                try:
                    out = seed(item, ytid, titles.get(item["url"]), expected[item["video_id"]])
                except Exception as e:
                    traceback.print_exc()
                    out = {"status": "skip", "reason": f"error: {e!r}"}
            out["seconds"] = round(time.time() - t0, 1)
            report[ytid] = {"video_id": item["video_id"], **out}
            save_json(report_path, report)
            print(ytid, out, flush=True)
    finally:
        llm.stop()

    hits = {}
    for item in items:
        ytid = parse_qs(urlsplit(item["url"]).query)["v"][0]
        hits[ytid] = hit(ytid)
        print(ytid, "HIT" if hits[ytid] else "MISS")
    cache.close()
    missed = [k for k, v in hits.items() if not v]
    print(f"HIT {len(hits) - len(missed)}/{len(hits)}")
    if missed:
        print("미완료:", " ".join(missed))


if __name__ == "__main__":
    main()
