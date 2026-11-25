import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

from config import BACKEND_DIR, DATA_DIR
from files import load_json, save_json


def extraction_to_mapping(claims_doc: dict, url=None, title=None) -> list[dict]:
    claims = []
    for claim in claims_doc["claims"]:
        claim_type = claim["claim_type"]
        claims.append({**claim, "claim_type": [claim_type] if isinstance(claim_type, str) else claim_type})
    return [{"video_id": claims_doc["video_id"], "url": url, "title": title,
             "products": claims_doc["products"], "claims": claims}]


def run(video_path: Path, run_dir: Path, url: str | None = None, title: str | None = None,
        new_session: bool = False) -> list[dict]:
    video_path = Path(video_path).resolve()
    out_dir = run_dir / "01_extraction"
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.iterdir():
        if old.is_file():
            old.unlink()
    marker = out_dir / ".started"
    marker.write_bytes(b"")
    started = marker.stat().st_mtime
    env = {k: v for k, v in os.environ.items() if k != "VIDEO_TITLE"}
    if title:
        env["VIDEO_TITLE"] = title
    subprocess.run([sys.executable, str(BACKEND_DIR / "claim_process" / "claim_extraction" / "main.py"), str(video_path)],
                   check=True, cwd=BACKEND_DIR, start_new_session=new_session, env=env)
    stem = video_path.stem
    for path in (DATA_DIR / "output").glob(glob.escape(stem) + ".*.json"):
        if "." not in path.name[len(stem) + 1:-5] and path.stat().st_mtime >= started:
            shutil.copy2(path, out_dir / path.name)
    videos = extraction_to_mapping(load_json(out_dir / f"{stem}.claims.json"), url=url, title=title)
    save_json(run_dir / "01_claims.json", videos)
    return videos
