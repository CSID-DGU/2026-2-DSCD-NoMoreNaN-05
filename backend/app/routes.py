import os

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel

from files import load_json

from . import cache, docs, jobs, result, video, worker
from .errors import ApiError, ok

router = APIRouter(prefix="/api")


class JobRequest(BaseModel):
    url: str


@router.post("/jobs", status_code=201, responses=docs.CREATE_JOB)
def create_job(req: JobRequest):
    jobs.sweep(jobs.now())
    video.check_url(req.url)
    video_id, title, duration = video.probe(req.url)
    job = None
    try:
        job = jobs.create(req.url, video_id, title, duration)
        hit = cache.restore_into(video_id, jobs.RUNS_DIR / job["job_id"])
        if hit:
            job = jobs.set_done(job["job_id"], cached=True)
        else:
            worker.submit(job["job_id"])
    except Exception:
        if job:
            jobs.remove(job["job_id"])
        raise ApiError("JOB_001") from None
    return ok({k: job[k] for k in ("job_id", "url", "created_at", "expires_at")}, 201)


@router.get("/jobs/{job_id}", responses=docs.GET_JOB)
def get_job(job_id: str):
    return ok(jobs.view(jobs.load(job_id), jobs.now()))


@router.get("/jobs/{job_id}/video", response_class=FileResponse, responses=docs.GET_VIDEO)
def get_video(job_id: str):
    job = jobs.load(job_id)
    if not jobs.view(job, jobs.now())["video"]["ready"]:
        raise ApiError("JOB_003")
    path = jobs.RUNS_DIR / job_id / f"{job['video']['video_id']}.mp4"
    try:
        st = os.stat(path)
    except FileNotFoundError:
        raise ApiError("JOB_003") from None
    return FileResponse(path, media_type="video/mp4", stat_result=st)


@router.get("/jobs/{job_id}/result", responses=docs.GET_RESULT)
def get_result(job_id: str):
    job = jobs.load(job_id)
    status = jobs.shown(job, jobs.now())["status"]
    if status in ("QUEUED", "PROCESSING"):
        raise ApiError("JOB_004")
    if status == "FAILED":
        raise ApiError("JOB_005")
    return ok(result.to_response(load_json(jobs.RUNS_DIR / job_id / "04_final_results.json"), job))
