"""입력 json → A 판정 결과 + 집계. 로컬 실행용 진입점.

    python -m claim_verification.claim_types.run input out_dir

input은 영상 목록 json 파일이나 영상별 json이 있는 폴더다. out_dir에 results.json과 summary.json을 쓴다.
summary의 for_b는 confirmed 제품의 클레임 중 EFFECT가 붙고 면책 문구가 아닌 건수로, 메커니즘 B가 판정할 대상이다.
labels는 타입 조합별("COMPOSITION+QUANTITY")로 센다.
입력에 정답(gold_label)이 있으면 판정 전에 지운다. 정답 파일을 실행 입력으로 잘못 넣어도 예측에 섞이지 않게 한다.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from ..inputs import validate_videos
from .judge import judge_video

GOLD = "gold_label"


def load_videos(path: str | Path) -> list[dict]:
    """영상 목록 json이나 영상별 json 폴더를 읽고 형식을 확인한다(inputs.py)."""
    path = Path(path)
    if path.is_dir():
        videos = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(path.glob("*.json"))]
    else:
        videos = json.loads(path.read_text(encoding="utf-8"))
    validate_videos(videos)
    return videos


def strip_gold(videos: list[dict]) -> int:
    """클레임의 gold_label을 지우고 지운 건수를 돌려준다."""
    removed = 0
    for video in videos:
        for claim in video["claims"]:
            if claim.pop(GOLD, None) is not None:
                removed += 1
    return removed


def summarize(videos: list[dict], results: list[dict]) -> dict:
    labels, codes = defaultdict(Counter), defaultdict(Counter)
    skipped, violations = Counter(), []
    for result in results:
        skipped.update(s["reason"] for s in result["skipped"])
        for claim in result["claims"]:
            labels["+".join(claim["claim_type"])][claim["label"]] += 1
            codes[claim["label"]].update(claim["reason_codes"])
            if claim["label"] == "VIOLATION":
                violations.append({"video_id": result["video_id"], "claim_id": claim["claim_id"], "text": claim["text"],
                                   "reason_codes": claim["reason_codes"]})
    return {
        "videos": len(results),
        "claims": sum(len(v["claims"]) for v in videos),
        "judged": sum(len(r["claims"]) for r in results),
        "for_b": sum(len(r["for_b"]) for r in results),
        "skipped": dict(skipped),
        "labels": {t: dict(c) for t, c in sorted(labels.items())},
        "reason_codes": {label: dict(c.most_common()) for label, c in sorted(codes.items())},
        "violations": violations,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    videos = load_videos(argv[0])
    removed = strip_gold(videos)
    if removed:
        print(f"경고: 입력에 {GOLD} {removed}건이 있어 지우고 판정함", file=sys.stderr)
    results = [judge_video(v) for v in videos]
    summary = summarize(videos, results)
    out = Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"판정 {summary['judged']}건, B 대상 {summary['for_b']}건, 제외 {sum(summary['skipped'].values())}건", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
