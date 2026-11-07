"""입력 json → A 판정 + B 결과 합치기 → 최종 결과 파일.

    python -m claim_verification.final.run input.json b_result.json out_dir [b_source]

A는 이 자리에서 돌린다. B는 B 담당 결과 json({"results": [...]} 또는 목록)을 읽는다.
b_source에는 B 결과를 만든 코드 위치(브랜치@커밋 등)를 적는다. 최종 결과 파일 meta에 남는다.
out_dir에 final_results.json과 final_summary.json을 쓴다.
    final_results.json = {"meta", "videos": 영상·제품 공식 정보(DB 포함), "results": 클레임마다 한 건}
입력에 정답(gold_label)이 있으면 판정 전에 지운다.
"""

import json
import sys
from collections import Counter
from pathlib import Path

from ..claim_types.judge import judge_video
from ..claim_types.run import GOLD, load_videos, strip_gold
from .merge import LABELS, merge, video_info


def load_b(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["results"] if isinstance(data, dict) else data


def summarize(rows: list[dict]) -> dict:
    labels = Counter(r["final_label"] for r in rows)
    return {
        "claims": len(rows),
        "labels": {label: labels[label] for label in LABELS if labels[label]},
        "decided_by": dict(Counter("+".join(r["decided_by"]) or "SKIPPED" for r in rows)),
        "skipped": dict(Counter(r["skipped_reason"] for r in rows if r["skipped_reason"])),
    }


def main(argv: list[str]) -> int:
    if len(argv) not in (3, 4):
        print(__doc__, file=sys.stderr)
        return 2
    input_path, b_path, out_dir = argv[:3]
    videos = load_videos(input_path)
    removed = strip_gold(videos)
    if removed:
        print(f"경고: 입력에 {GOLD} {removed}건이 있어 지우고 판정함", file=sys.stderr)
    rows = merge(videos, [judge_video(v) for v in videos], load_b(b_path))
    meta = {"input": str(input_path), "b_result": str(b_path), "b_source": argv[3] if len(argv) == 4 else None,
            "db_version": sorted({v.get("db_version") for v in videos if v.get("db_version")}),
            "label_order": ["DISCLAIMER(먼저)", *LABELS[1:]]}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    final = {"meta": meta, "videos": [video_info(v) for v in videos], "results": rows}
    (out / "final_results.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = summarize(rows)
    (out / "final_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"최종 {summary['claims']}건: {summary['labels']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
