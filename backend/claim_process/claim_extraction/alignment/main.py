"""python main.py [영상.mp4 | 폴더 ...] [--branches audio,text,scene] [--title TITLE]   # 기본 data/ 전부, 브랜치 전부
영상마다 켠 브랜치의 data/output/<영상>.{audio_claims, visual_text_claims, visual_scene_claims}.json 필요"""
import argparse
import json
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from claim_process.claim_extraction.alignment.aligner import Aligner                      # noqa: E402
from claim_process.claim_extraction.alignment.hints import NameHints                      # noqa: E402
from claim_process.claim_extraction.common import LLMClient                               # noqa: E402
from config import REF_DSN                                                                # noqa: E402

INPUT_PATH = ROOT / "data"
OUTPUT_DIR = ROOT / "data" / "output"
FILES = {"audio": "audio_claims", "text": "visual_text_claims", "scene": "visual_scene_claims"}
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}     # audio·visual 입력 공통 확장자

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-oss-120b")
REASONING_EFFORT = "medium"

OVERLAP_MIN = 0.5          # 구간 겹침 ÷ 짧은 쪽 길이. 이 이상이면 시간 후보 쌍
DEDUP_SIM = 0.8            # 시각 무관 전역 후보: 그룹 대표 text(keep) 편집거리 유사도. 후보 검색에만 씀
JUDGE_CHUNK = 20           # 판정 한 호출에 넣는 Claim 쌍 수. 공유 KV 풀 16384 기준으로 계산(쌍당 ≈134 tok). 풀이 32768이 되어 여유가 늘었다
JUDGE_PARALLEL = 4         # 동시에 보내는 판정·유형 묶음 수 = llama-server n_slots
TYPE_CHUNK = 20            # 유형 한 호출에 넣는 최종 Claim 수
# scene 글자 복사 대조 전에 떼는 서술 접두어("화면 하단 문구:", "화면 하단 로고:" 등). 목록 밖 접두어가 붙은 복사는 판정으로 간다
SCENE_COPY_PREFIX = re.compile(r"^(화면|자막|하단|상단|중앙|로고|문구|글자|텍스트)[\s·]*(하단|상단|중앙)?[\s·]*"
                               r"(문구|자막|로고|글자|텍스트)?\s*[:：]\s*")


def load(stem: str, branch: str) -> dict:
    path = OUTPUT_DIR / f"{stem}.{FILES[branch]}.json"
    if not path.exists():
        sys.exit(f"{path} 없음 → 먼저 {branch} 브랜치를 실행")
    return json.loads(path.read_text(encoding="utf-8"))


def save(name: str, data: dict) -> None:
    out = OUTPUT_DIR / name
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  saved: {out.relative_to(ROOT)}")


def run(stem: str, branches: list[str], aligner: Aligner, title: str | None = None) -> None:
    print(f"\n=== [align] {stem}")
    data = {b: load(stem, b) for b in branches}
    print("  " + ", ".join(f"{b} claims: {len(d['claims'])}" for b, d in data.items()))

    if title:
        print(f"  title: {title}")
    products, claims, record = aligner.align(data, title)
    print(f"  products: {[p.product_name for p in products]}")
    for c in claims:
        print(f"    - {c.claim_id} [{c.claim_type}] {c.text}  ({c.t_start:.1f}~{c.t_end:.1f}s, {c.product_ref})")

    save(f"{stem}.claims.json", {"video_id": stem,
                                 "products": [asdict(p) for p in products],
                                 "claims": [asdict(c) for c in claims]})
    save(f"{stem}.alignment.json", {**record, "title": title})


def branch_list(s: str) -> list[str]:
    bs = s.split(",")
    bad = [b for b in bs if b not in FILES]
    if bad:
        raise argparse.ArgumentTypeError(f"{bad} 없음 (choose from {', '.join(FILES)})")
    return bs


def main():
    p = argparse.ArgumentParser(usage=__doc__)
    p.add_argument("target", nargs="*", type=Path, default=[INPUT_PATH])
    p.add_argument("--branches", type=branch_list, default="audio,text,scene")
    p.add_argument("--title", default=os.environ.get("VIDEO_TITLE") or None, help="영상 제목 (기본 환경변수 VIDEO_TITLE)")
    args = p.parse_args()
    branches = args.branches
    videos = [v for t in args.target
              for v in ([t] if t.is_file() else sorted(v for v in t.iterdir() if v.suffix.lower() in VIDEO_EXTS))]
    if not videos:
        sys.exit(f"입력 영상이 없음: {args.target}")
    if args.title and len(videos) > 1:
        sys.exit("--title는 영상 1편일 때만")

    aligner = Aligner(LLMClient(LLM_BASE_URL, LLM_MODEL, reasoning_effort=REASONING_EFFORT), OVERLAP_MIN, DEDUP_SIM,
                      JUDGE_CHUNK, JUDGE_PARALLEL, SCENE_COPY_PREFIX, TYPE_CHUNK, NameHints.from_db(REF_DSN))
    for v in videos:
        run(v.stem, branches, aligner, args.title)


if __name__ == "__main__":
    main()
