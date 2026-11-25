import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from config import RUNS_DIR


def new_run_dir() -> Path:
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:6]
    path = RUNS_DIR / run_id
    path.mkdir(parents=True)
    return path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(path, obj) -> None:
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
