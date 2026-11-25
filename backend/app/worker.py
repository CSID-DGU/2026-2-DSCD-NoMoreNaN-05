import queue
import threading
import traceback

from claim_process.claim_extraction import extraction
from claim_process.claim_verification import adapters, product_mapping

from . import cache, jobs, llm, video

_queue: queue.Queue | None = None
_thread: threading.Thread | None = None
_stopping = threading.Event()


def start() -> None:
    global _queue, _thread, _stopping
    _stopping = threading.Event()
    _queue = queue.Queue()
    _thread = threading.Thread(target=loop, daemon=True)
    _thread.start()


def stop() -> None:
    _stopping.set()
    _queue.put(None)
    _thread.join()


def submit(job_id: str) -> None:
    _queue.put(job_id)


def loop() -> None:
    while True:
        job_id = _queue.get()
        if job_id is None or _stopping.is_set():
            return
        try:
            process(job_id)
        except Exception:
            traceback.print_exc()


def fetch(job: dict) -> None:
    video.download(job["url"], jobs.RUNS_DIR / job["job_id"], job["video"]["video_id"])


def extract(job: dict) -> list[dict]:
    run_dir = jobs.RUNS_DIR / job["job_id"]
    return extraction.run(run_dir / f"{job['video']['video_id']}.mp4", run_dir, url=job["url"],
                          title=job["video"]["title"], new_session=True)


def mapping(job: dict, videos: list[dict]) -> list[dict]:
    run_dir = jobs.RUNS_DIR / job["job_id"]
    return product_mapping.run(videos, run_dir, input_path=run_dir / "01_claims.json")


def verdicts(job: dict, videos: list[dict]) -> None:
    from claim_process.claim_verification import verdict_a, verdict_b

    run_dir = jobs.RUNS_DIR / job["job_id"]
    b = verdict_b.run(videos, run_dir)
    verdict_a.run(videos, adapters.b_records(b), run_dir, input_path=run_dir / "02_claims_with_db.json",
                  b_path=run_dir / "03_verdict_b.json")


def explain(job: dict) -> None:
    from claim_process.claim_verification import explanation

    explanation.run(jobs.RUNS_DIR / job["job_id"])


def mapping_all_failed(videos: list[dict]) -> bool:
    v = videos[0]
    no_confirmed = not any(p["match"]["status"] == "confirmed" for p in v["products"])
    no_ref = all(c.get("product_ref") is None for c in v["claims"])
    return no_confirmed or no_ref


def process(job_id: str) -> None:
    try:
        job = jobs.load_raw(job_id)
        if job is None or jobs.expired(job, jobs.now()):
            raise jobs.Cancelled(job_id)
        run_dir = jobs.RUNS_DIR / job_id
        video_id = job["video"]["video_id"]
        try:
            hit = cache.restore_into(video_id, run_dir)
        except Exception:
            traceback.print_exc()
            for name in ("04_final_results.json", f"{video_id}.mp4"):
                (run_dir / name).unlink(missing_ok=True)
            hit = False
        if hit:
            jobs.set_done(job_id, cached=True)
            return
        job = jobs.set_running(job_id, 1)
        try:
            fetch(job)
        except Exception:
            jobs.set_failed(job_id, 1, "VIDEO_FETCH_FAILED")
            return
        job = jobs.set_running(job_id, 2)
        try:
            llm.wait()
            videos = extract(job)
        except Exception:
            jobs.set_failed(job_id, 2, "CLAIM_EXTRACT_FAILED")
            return
        job = jobs.set_running(job_id, 3)
        if not videos[0]["claims"]:
            jobs.set_failed(job_id, 3, "NO_CLAIMS")
            return
        try:
            videos = mapping(job, videos)
            if mapping_all_failed(videos):
                jobs.set_failed(job_id, 3, "PRODUCT_MAPPING_ALL")
                return
            verdicts(job, videos)
            explain(job)
        except Exception:
            jobs.set_failed(job_id, 3, "VERIFY_FAILED")
            return
        job = jobs.set_done(job_id)
        try:
            cache.publish(job)
        except Exception:
            traceback.print_exc()
    except jobs.Cancelled:
        jobs.remove(job_id)
