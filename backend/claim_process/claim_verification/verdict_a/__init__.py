import sys

from files import save_json

from .claim_verification.claim_types.judge import judge_video
from .claim_verification.claim_types.run import GOLD, strip_gold
from .claim_verification.final.merge import LABELS, merge, video_info
from .claim_verification.final.run import summarize
from .claim_verification.inputs import validate_videos


def run(videos: list[dict], b_records: list[dict], run_dir, input_path=None, b_path=None, b_source=None) -> dict:
    validate_videos(videos)
    removed = strip_gold(videos)
    if removed:
        print(f"경고: 입력에 {GOLD} {removed}건이 있어 지우고 판정함", file=sys.stderr)
    rows = merge(videos, [judge_video(v) for v in videos], b_records)
    meta = {"input": str(input_path) if input_path else None, "b_result": str(b_path) if b_path else None,
            "b_source": b_source,
            "db_version": sorted({v.get("db_version") for v in videos if v.get("db_version")}),
            "label_order": ["DISCLAIMER(먼저)", *LABELS[1:]]}
    final = {"meta": meta, "videos": [video_info(v, rows) for v in videos], "results": rows}
    save_json(run_dir / "04_final_results.json", final)
    summary = summarize(rows)
    save_json(run_dir / "04_final_summary.json", summary)
    print(f"최종 {summary['claims']}건: {summary['labels']}", file=sys.stderr)
    return final
