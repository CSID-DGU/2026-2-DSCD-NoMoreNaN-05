"""handoff json(영상 1편) → 결과 json. 로컬 실행용 진입점.

    python -m claim_verification.run handoff.json [result.json]

result.json을 주지 않으면 결과를 화면에 출력한다. 라벨별 개수는 stderr로 출력한다.
"""

import json
import sys
from collections import Counter
from pathlib import Path

from .inputs import load_handoff
from .judge import judge_video


def main(argv: list[str]) -> int:
    if len(argv) not in (1, 2):
        print(__doc__, file=sys.stderr)
        return 2
    result = judge_video(load_handoff(argv[0]))
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if len(argv) == 2:
        Path(argv[1]).write_text(text, encoding="utf-8")
    else:
        print(text)
    labels = Counter(c["label"] for c in result["claims"])
    print(f"{result['video_id']} {result['status']} {dict(labels)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
