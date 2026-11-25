import json
import shutil
import threading
from datetime import UTC, datetime, timedelta
from itertools import accumulate

from config import CACHE_STEP_DELAY_SEC, JOB_TTL_HOURS, RUNS_DIR
from files import new_run_dir

from .errors import ApiError

STEPS = ("영상 가져오기", "주장 추출", "주장 검증")
RESTART = {1: "VIDEO_FETCH_FAILED", 2: "CLAIM_EXTRACT_FAILED", 3: "VERIFY_FAILED"}
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LOCK = threading.Lock()


class Cancelled(Exception):
    pass


def now() -> datetime:
    return datetime.now(UTC)


def stamp(t: datetime) -> str:
    return t.strftime(TIME_FORMAT)


def parse(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _write(run_dir, job: dict) -> None:
    tmp = run_dir / "job.json.tmp"
    tmp.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(run_dir / "job.json")


def create(url: str, video_id: str, title: str | None, duration: float | None) -> dict:
    with LOCK:
        run_dir = new_run_dir()
        created = now().replace(microsecond=0)
        job = {"job_id": run_dir.name, "url": url,
               "video": {"video_id": video_id, "title": title, "duration_sec": duration},
               "status": "QUEUED", "current_step": 1, "failure": None,
               "created_at": stamp(created), "finished_at": None,
               "expires_at": stamp(created + timedelta(hours=JOB_TTL_HOURS)), "cached": False}
        try:
            _write(run_dir, job)
        except Exception:
            shutil.rmtree(run_dir, ignore_errors=True)
            raise
    return job


def update(job_id: str, **fields) -> dict:
    with LOCK:
        job = load_raw(job_id)
        if job is None or expired(job, now()):
            raise Cancelled(job_id)
        job.update(fields)
        _write(RUNS_DIR / job_id, job)
    return job


def remove(job_id: str) -> None:
    with LOCK:
        shutil.rmtree(RUNS_DIR / job_id, ignore_errors=True)


def load_raw(job_id: str) -> dict | None:
    try:
        return json.loads((RUNS_DIR / job_id / "job.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def load(job_id: str) -> dict:
    job = load_raw(job_id)
    if job is None:
        raise ApiError("JOB_002")
    if expired(job, now()):
        remove(job_id)
        raise ApiError("JOB_002")
    return job


def set_running(job_id: str, step: int) -> dict:
    return update(job_id, status="PROCESSING", current_step=step)


def set_failed(job_id: str, step: int, code: str) -> dict:
    return update(job_id, status="FAILED", current_step=step, failure={"step": step, "code": code},
                  finished_at=stamp(now()))


def set_done(job_id: str, cached: bool = False) -> dict:
    finished = now() + timedelta(seconds=sum(CACHE_STEP_DELAY_SEC)) if cached else now()
    return update(job_id, status="DONE", current_step=None, cached=cached, finished_at=stamp(finished))


def shown(job: dict, t: datetime) -> dict:
    """캐시 적중 작업이 아직 지연 창 안이면 진행 중으로 보이는 사본을 돌려준다."""
    total = sum(CACHE_STEP_DELAY_SEC)
    if job["status"] != "DONE" or not job.get("cached") or total <= 0 or t >= parse(job["finished_at"]):
        return job
    elapsed = (t - (parse(job["finished_at"]) - timedelta(seconds=total))).total_seconds()
    step = 1 + sum(elapsed >= bound for bound in accumulate(CACHE_STEP_DELAY_SEC[:2]))
    return {**job, "status": "PROCESSING", "current_step": step, "finished_at": None}


def view(job: dict, t: datetime) -> dict:
    job = shown(job, t)
    status = job["status"]
    done = 3 if status == "DONE" else job["current_step"] - 1
    active = {"PROCESSING": "RUNNING", "FAILED": "FAILED"}.get(status, "PENDING")
    steps = [{"no": i + 1, "name": name, "state": "DONE" if i < done else active if i == done else "PENDING"}
             for i, name in enumerate(STEPS)]
    end = parse(job["finished_at"]) if job["finished_at"] else t
    return {"job_id": job["job_id"], "url": job["url"], "status": status, "current_step": job["current_step"],
            "completed_steps": done, "steps": steps, "failure": job["failure"],
            "video": {"title": job["video"]["title"], "duration_sec": job["video"]["duration_sec"],
                      "ready": done >= 1},
            "elapsed_sec": (end - parse(job["created_at"])).total_seconds(),
            "created_at": job["created_at"], "finished_at": job["finished_at"], "expires_at": job["expires_at"]}


def expired(job: dict, t: datetime) -> bool:
    return t > parse(job["expires_at"])


def sweep(t: datetime) -> None:
    for path in list(RUNS_DIR.glob("*/job.json")):
        job = load_raw(path.parent.name)
        if job is not None and expired(job, t):
            remove(path.parent.name)


def restore(t: datetime) -> None:
    sweep(t)
    for path in list(RUNS_DIR.glob("*/job.json")):
        job_id = path.parent.name
        job = load_raw(job_id)
        if job is None or job["status"] not in ("QUEUED", "PROCESSING"):
            continue
        try:
            set_failed(job_id, job["current_step"], RESTART[job["current_step"]])
        except Cancelled:
            remove(job_id)
