"""클레임 파일 + data.csv → 영상별 판정 입력 JSON.

    python -m claim_verification.claim_types.handoff.build claims.json data.csv out_dir
"""

import csv
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from .fields import product_db
from .match import ProductIndex

csv.field_size_limit(10**9)


def load_rows(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def build_product(product: dict, index: ProductIndex) -> dict:
    status, method, row, candidates = index.match(product)
    out = dict(product)
    out["match"] = {"status": status, "method": method, "candidates": candidates,
                    "matched_name": row["PRDUCT"] if row else None,
                    "matched_company": row["ENTRPS"] if row else None}
    out["DB"] = product_db(row) if row else None
    if row:
        out["manufacturing_report_number"] = row["STTEMNT_NO"]
    return out


def build_video(video: dict, index: ProductIndex, db_version: str) -> dict:
    return {"video_id": video["video_id"], "url": video.get("url"), "db_version": db_version,
            "products": [build_product(p, index) for p in video["products"]],
            "claims": video["claims"]}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    claims_path, csv_path, out_dir = argv
    videos = json.loads(Path(claims_path).read_text(encoding="utf-8"))
    ids = Counter(v["video_id"] for v in videos)
    duplicated = [i for i, n in ids.items() if n > 1]
    if duplicated:
        raise ValueError(f"video_id 중복: {duplicated[:5]}")
    index = ProductIndex(load_rows(csv_path))
    db_version = f"data.csv@{date.fromtimestamp(Path(csv_path).stat().st_mtime).isoformat()}"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    statuses = Counter()
    for video in videos:
        built = build_video(video, index, db_version)
        statuses.update(p["match"]["status"] for p in built["products"])
        (out / f"{video['video_id']}.json").write_text(json.dumps(built, ensure_ascii=False), encoding="utf-8")
    print(f"영상 {len(videos)}편, 제품 {dict(statuses)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
