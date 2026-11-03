"""평가에 쓸 영상을 정해진 수만큼 고른다. 판정 결과를 보지 않고 영상 내용만으로 뺀다.

    python -m claim_verification.scripts.select_videos input.json output.json excluded.json 501

뺄 영상의 순서: 판정할 수 있는 클레임 수 → 전체 클레임 수 → 제품 수 → video_id가 작은 것부터.
판정할 수 있는 클레임은 이름이 있는 제품을 가리키는 QUANTITY·COMPOSITION·CERTIFICATION·EFFECT다.
match.status는 보지 않는다. 제품 매칭 기준이 바뀌어도 같은 영상을 고르게 하기 위해서다.
"""

import json
import sys
from pathlib import Path

OBJECTIVE_TYPES = {"QUANTITY", "COMPOSITION", "CERTIFICATION", "EFFECT"}


def usable_claims(video: dict) -> int:
    named = {p["product_ref"] for p in video["products"] if p.get("product_name")}
    return sum(1 for c in video["claims"] if c.get("product_ref") in named and c.get("claim_type") in OBJECTIVE_TYPES)


def _order(video: dict) -> tuple:
    return usable_claims(video), len(video["claims"]), len(video["products"]), video["video_id"]


def select(videos: list[dict], keep: int) -> tuple[list[dict], list[dict]]:
    """(남길 영상, 뺄 영상). 남길 영상은 입력 순서를 유지한다."""
    if keep > len(videos):
        raise ValueError(f"영상이 {len(videos)}개라 {keep}개를 남길 수 없음")
    removed = sorted(videos, key=_order)[:len(videos) - keep]
    removed_ids = {v["video_id"] for v in removed}
    return [v for v in videos if v["video_id"] not in removed_ids], removed


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    videos = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    kept, removed = select(videos, int(argv[3]))
    Path(argv[1]).write_text(json.dumps(kept, ensure_ascii=False), encoding="utf-8")
    report = [{"video_id": v["video_id"], "url": v.get("url"), "usable_claims": usable_claims(v), "claims": len(v["claims"]),
               "products": [p.get("product_name") for p in v["products"]]} for v in removed]
    Path(argv[2]).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(videos)}편 → {len(kept)}편, 제외 {len(removed)}편", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
