"""Run the full mapping job, export handoffs and validate before marking complete."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/processed/claim_evidence_all"


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@contextmanager
def lock_run(directory):
    stream = (directory / "job.lock").open("a+b")
    stream.seek(0)
    if not stream.read(1):
        stream.write(b"0")
        stream.flush()
    stream.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        stream.close()
        raise RuntimeError("Another full mapping job already holds the lock.") from None
    try:
        yield
    finally:
        stream.close()


def validate(directory, expected_claims, expected_videos, input_sha):
    ranked_path = directory / "claim_evidence_ranked.json"
    ranked = json.loads(ranked_path.read_text(encoding="utf-8"))
    claims = [claim for video in ranked["videos"] for claim in video["claims"]]
    if len(claims) != expected_claims or len(ranked["videos"]) != expected_videos:
        raise RuntimeError("Output does not contain every input video/claim.")
    if ranked["metadata"]["input_sha256"] != input_sha:
        raise RuntimeError("Input signature differs.")
    for claim in claims:
        candidates = claim["ranked_evidences"]
        scores = [row["reranker_raw_score"] for row in candidates]
        if scores != sorted(scores, reverse=True) or not all(map(math.isfinite, scores)):
            raise RuntimeError("Invalid relevance ordering/scores.")
        if claim["candidate_count"] != len(candidates) or claim["judgment"]["verdict"] is not None:
            raise RuntimeError("Candidate count or verdict validation failed.")
        if claim["product_match_status"] != "matched" and any(row["material_scope"] == "product_direct" for row in candidates):
            raise RuntimeError("Unmatched product has direct-product evidence.")
        if not candidates and claim["retrieval_status"] != "no_linkable_evidence":
            raise RuntimeError("Missing no-evidence marker.")
        if any(row["relationship"] != row["material_scope"] for row in candidates):
            raise RuntimeError("Unexpected relationship label.")
    for k in (1, 3, 5):
        handoff = json.loads((directory / f"top{k}_handoff.json").read_text(encoding="utf-8"))
        exported = [claim for video in handoff["videos"] for claim in video["claims"]]
        if len(exported) != expected_claims:
            raise RuntimeError("Incomplete Top-K handoff.")
        if any(len(out["evidences"]) != min(k, original["candidate_count"]) for out, original in zip(exported, claims)):
            raise RuntimeError("Top-K handoff does not match measured ranks.")
        del handoff, exported
    return ranked["summary"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with lock_run(OUTPUT):
        raw = args.input.read_bytes()
        source = json.loads(raw.decode("utf-8-sig"))
        claim_count = sum(len(video.get("claims", [])) for video in source)
        video_count = len(source)
        input_sha = hashlib.sha256(raw).hexdigest()
        del raw, source
        status = dict(status="starting", pid=os.getpid(), started_at=datetime.now(timezone.utc).isoformat(),
                      claim_count=claim_count, video_count=video_count,
                      input_sha256=input_sha, threads=args.threads)
        status_path = OUTPUT / "full_run_status.json"
        save(status_path, status)
        pilot = ROOT / "data/processed/claim_evidence_pilot100"
        revision = json.loads((pilot / "model_revision.json").read_text(encoding="utf-8"))["revision"]
        command = [sys.executable, "-u", "-X", "utf8", str(ROOT / "scripts/run_claim_evidence_pilot.py"),
                   "--input", str(args.input.resolve()), "--claim-limit", str(claim_count),
                   "--output-dir", str(OUTPUT), "--threads", str(args.threads),
                   "--batch-size", str(args.batch_size), "--reuse-cache", str(pilot / "reranker_scores.sqlite"),
                   "--revision", revision, "--offline-model"]
        try:
            worker = subprocess.Popen(command, cwd=ROOT)
            status.update(status="scoring", worker_pid=worker.pid)
            save(status_path, status)
            code = worker.wait()
            if code:
                raise RuntimeError(f"Scoring process exited with code {code}; saved scores can be resumed.")
            status.update(status="exporting")
            save(status_path, status)
            subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/summarize_claim_evidence_pilot.py"),
                            "--output-dir", str(OUTPUT)], check=True, cwd=ROOT)
            status.update(status="validating")
            save(status_path, status)
            summary = validate(OUTPUT, claim_count, video_count, input_sha)
            if hashlib.sha256(args.input.read_bytes()).hexdigest() != input_sha:
                raise RuntimeError("Input changed while the job was running.")
            status.update(status="complete", finished_at=datetime.now(timezone.utc).isoformat(), summary=summary,
                          result=str(OUTPUT / "top3_handoff.json"))
            save(status_path, status)
            print(json.dumps(status, ensure_ascii=False), flush=True)
            return 0
        except Exception as error:
            status.update(status="failed", error=str(error), resumable=True)
            save(status_path, status)
            raise


if __name__ == "__main__":
    raise SystemExit(main())
