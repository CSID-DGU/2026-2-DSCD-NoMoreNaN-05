import argparse
from pathlib import Path

from app import llm
from claim_process.claim_extraction import extraction
from claim_process.claim_verification import (
    adapters,
    explanation,
    product_mapping,
    verdict_a,
    verdict_b,
)
from files import new_run_dir


def main():
    parser = argparse.ArgumentParser(description="영상 1편 → 추출 → 제품 매핑 → 판정 B → 판정 A+병합 → 설명문")
    parser.add_argument("video", type=Path)
    parser.add_argument("--url")
    parser.add_argument("--title")
    parser.add_argument("--b-source")
    args = parser.parse_args()

    run_dir = new_run_dir()
    try:
        llm.wait()
        videos = extraction.run(args.video, run_dir, url=args.url, title=args.title)
        videos = product_mapping.run(videos, run_dir, input_path=run_dir / "01_claims.json")
        b = verdict_b.run(videos, run_dir)
        verdict_a.run(videos, adapters.b_records(b), run_dir, input_path=run_dir / "02_claims_with_db.json",
                      b_path=run_dir / "03_verdict_b.json", b_source=args.b_source)
        explanation.run(run_dir)
    finally:
        llm.stop()
    print(run_dir)


if __name__ == "__main__":
    main()
