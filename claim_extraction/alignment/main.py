"""python main.py [영상.mp4 | 폴더]   # 기본 data/ 전부. 영상마다 data/output/<영상>.audio_claims.json + .visual_claims.json 필요"""
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
INPUT_PATH = ROOT / "data"
from claim_extraction.alignment.aligner import Aligner                      # noqa: E402
from claim_extraction.alignment.llm import LLMClient                        # noqa: E402
OUTPUT_DIR = ROOT / "data" / "output"

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")
REASONING_EFFORT = "medium"

OVERLAP_MIN = 0.5          # 구간 겹침 ÷ 짧은 쪽 길이. 이 이상이면 후보 쌍
ROUGE_MIN = 0.8            # 글자 ROUGE-L(짧은 쪽 recall). 이 이상이면 병합
MIN_CHARS = 3              # 병합 비교 시 짧은 쪽 최소 글자 수
DEICTIC = ("이 제품", "이거", "이것", "요거", "이 영양제")   # target을 product로 채우는 지시어


def load(stem: str, kind: str) -> dict:
    path = OUTPUT_DIR / f"{stem}.{kind}_claims.json"
    if not path.exists():
        sys.exit(f"{path} 없음 → 먼저 {kind} 파트를 실행")
    return json.loads(path.read_text(encoding="utf-8"))


def run(stem: str, aligner: Aligner) -> Path:
    print(f"\n=== [align] {stem}")
    audio, visual = load(stem, "audio"), load(stem, "visual")
    print(f"  audio claims: {len(audio['claims'])}, visual claims: {len(visual['claims'])}")

    result = aligner.align(audio, visual)
    claims = result["claims"]
    print(f"  claims: {len(claims)}, product={result['product']!r}, ingredient={result['ingredient']}")
    for c in claims:
        flag = f" ⚠{c.conflict}" if c.conflict else ""
        print(f"    - {c.claim_id} [{c.source}] {c.text}  ({c.t_start:.1f}~{c.t_end:.1f}s, {c.scope}, target={c.target}){flag}")

    out = OUTPUT_DIR / f"{stem}.claims.json"
    out.write_text(json.dumps({
        "video_id": audio.get("video_id", stem),
        "video": audio.get("video"),
        "transcript": audio["transcript"],
        "screen_texts": visual.get("screen_texts", []),
        "product": result["product"],
        "ingredient": result["ingredient"],
        "brand": result["brand"],
        "claims": [asdict(c) for c in claims],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  saved: {out.relative_to(ROOT)}")
    return out


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_PATH
    videos = [target] if target.is_file() else sorted(p for p in target.iterdir() if p.suffix.lower() == ".mp4")
    if not videos:
        sys.exit(f"입력 영상이 없음: {target}")
    stems = [v.stem for v in videos]

    aligner = Aligner(LLMClient(LLM_BASE_URL, LLM_MODEL, reasoning_effort=REASONING_EFFORT),
                      OVERLAP_MIN, ROUGE_MIN, MIN_CHARS, DEICTIC)
    for s in stems:
        run(s, aligner)


if __name__ == "__main__":
    main()
