"""입력 json → A 판정 결과 + 집계. 로컬 실행용 진입점.

    python -m claim_verification.claim_types.run input out_dir

input은 영상 목록 json 파일이나 영상별 json이 있는 폴더다. out_dir에 results.json과 summary.json을 쓴다.
summary의 for_b는 confirmed 제품의 EFFECT 중 면책 문구를 뺀 건수로, 메커니즘 B가 판정할 대상이다.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from .judge import EFFECT, judge_video


def load_videos(path: str | Path) -> list[dict]:
    path = Path(path)
    if path.is_dir():
        return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(path.glob("*.json"))]
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(videos: list[dict], results: list[dict]) -> dict:
    labels, codes = defaultdict(Counter), defaultdict(Counter)
    skipped, violations = Counter(), []
    for result in results:
        skipped.update(s["reason"] for s in result["skipped"])
        for claim in result["claims"]:
            labels[claim["claim_type"]][claim["label"]] += 1
            codes[claim["label"]].update(claim["reason_codes"])
            if claim["label"] == "VIOLATION":
                violations.append({"video_id": result["video_id"], "claim_id": claim["claim_id"], "text": claim["text"],
                                   "reason_codes": claim["reason_codes"]})
    return {
        "videos": len(results),
        "claims": sum(len(v["claims"]) for v in videos),
        "judged": sum(len(r["claims"]) for r in results),
        "for_b": _count_for_b(videos, results),
        "skipped": dict(skipped),
        "labels": {t: dict(c) for t, c in sorted(labels.items())},
        "reason_codes": {label: dict(c.most_common()) for label, c in sorted(codes.items())},
        "violations": violations,
    }


def _count_for_b(videos: list[dict], results: list[dict]) -> int:
    count = 0
    for video, result in zip(videos, results):
        confirmed = {p["product_ref"] for p in result["products"] if p["match_status"] == "confirmed"}
        in_a = {c["claim_id"] for c in result["claims"]}
        count += sum(1 for c in video["claims"] if c.get("claim_type") == EFFECT
                     and c.get("product_ref") in confirmed and c["claim_id"] not in in_a)
    return count


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    videos = load_videos(argv[0])
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
