from claim_process.claim_verification.verdict_a.claim_verification.final.merge import (
    LABELS,
)


def to_response(final: dict, job: dict) -> dict:
    video = final["videos"][0]
    labels = {k: video["summary"]["labels"].get(k, 0) for k in LABELS}
    claims = [{k: v for k, v in r.items() if k != "video_id"}
              for r in final["results"] if r["video_id"] == video["video_id"]]
    db = final["meta"]["db_version"]
    return {"job_id": job["job_id"],
            "video": {"video_id": video["video_id"], "url": video["url"], "title": video["title"],
                      "duration_sec": job["video"]["duration_sec"]},
            "products": video["products"],
            "summary": {"claims": video["summary"]["claims"], "labels": labels},
            "popup_summary": video.get("popup_summary"),
            "claims": claims,
            "meta": {"db_version": db[0] if db else None, "label_order": list(LABELS)}}
