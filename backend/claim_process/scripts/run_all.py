import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse
import shutil

from claim_process.claim_verification import (
    adapters,
    explanation,
    product_mapping,
    verdict_a,
    verdict_b,
)
from files import load_json, new_run_dir


def main():
    parser = argparse.ArgumentParser(description="기존 JSON에서 시작해 끝까지 실행")
    parser.add_argument("--from", dest="start", choices=["claims", "claims_with_db"], required=True)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()

    run_dir = new_run_dir()
    if args.start == "claims":
        shutil.copyfile(args.input, run_dir / "01_claims.json")
        videos = product_mapping.run(load_json(args.input), run_dir, input_path=run_dir / "01_claims.json")
    else:
        shutil.copyfile(args.input, run_dir / "02_claims_with_db.json")
        videos = load_json(args.input)
    b = verdict_b.run(videos, run_dir)
    verdict_a.run(videos, adapters.b_records(b), run_dir, input_path=run_dir / "02_claims_with_db.json",
                  b_path=run_dir / "03_verdict_b.json")
    explanation.run(run_dir)
    print(run_dir)


if __name__ == "__main__":
    main()
