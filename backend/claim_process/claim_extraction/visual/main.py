"""python main.py keyframes [--select change,text] [--ocr] [영상.mp4 | 폴더 ...]   # VLM 입력 프레임 선택 · OCR 글자 구간
python main.py text  [영상.mp4 | 폴더 ...]   # 글자 구간 → gpt-oss (serve_llm.sh 서버 필요). 기본 OFF, 되돌림용
python main.py scene [영상.mp4 | 폴더 ...]   # 프레임 + 구간 OCR 줄 → Qwen3.5 (serve_vlm.sh 서버 필요)

--select: change = V-JEPA 2 변화 프레임, text = OCR 글자 구간의 대표 표기 프레임. 둘 다면 합집합.
--ocr: text 선택기 없이도 OCR 글자 구간(text_spans)을 만든다(text 브랜치용)."""
import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from claim_process.claim_extraction.common import LLMClient                               # noqa: E402
from claim_process.claim_extraction.visual.claim import (VLM, SceneClaimExtractor,        # noqa: E402
                                           TextClaimExtractor)
from claim_process.claim_extraction.visual.keyframe import (ChangeDetector, Frame, TextDetector,  # noqa: E402
                                              VideoReader, candidates, list_inputs)
from claim_process.claim_extraction.visual.keyframe.text import rep_frames                 # noqa: E402

# ── 입출력 ─────────────────────────────────────────────
INPUT_PATH = ROOT / "data"
OUTPUT_DIR = ROOT / "data" / "output"
FRAME_DIR = ROOT / "data" / "frames"        # VLM 입력 프레임 이미지

# ── Keyframe Selection ─────────────────────────────────
CHANGE_MODEL = "facebook/vjepa2-vitg-fpc64-384"
OCR_MODEL = "PaddlePaddle/PaddleOCR-VL-1.6"
SMALL_DEVICE = "cuda:0"                     # V-JEPA 2, OCR 올릴 카드

SAMPLE_INTERVAL = 0.5                       # 변화 후보 프레임 간격(초). 영상 전체 균등
CHANGE_THRESHOLD = 0.10                     # 1 - cosine. 이 이상 달라야 새 프레임
MAX_KEYFRAMES = 25                          # 변화 프레임 상한(change 선택기 전용)
OCR_INTERVAL = 0.5                          # 원본 전체 OCR 간격(초)
OCR_SIM_MIN = 0.8                           # 줄 편집거리 유사도. 이 이상이면 같은 글자 구간
OCR_BATCH = 8                               # 한 번에 OCR할 프레임 수. use_cache=True에서 1 → 1.73초/장, 8 → 0.42초/장 (사용자 결정 10-26)
OCR_MAX_PIXELS = 1280 * 28 * 28             # OCR 입력 최대 픽셀 (모델 카드 OCR 값 = preprocessor_config 기본값)
VJEPA_FRAMES = 16                           # V-JEPA 64프레임 창에서 솎아 넣을 프레임 수. 클립당 2.91 → 0.82초

# ── Claim 추출 서버 ────────────────────────────────────
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-oss-120b")
VLM_BASE_URL = os.environ.get("VLM_BASE_URL", "http://localhost:8002/v1")


def save(name: str, data: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / name
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  saved: {out.relative_to(ROOT)}")


def merge_frames(*lists: list[Frame]) -> list[Frame]:
    """선택기 결과의 합집합. 같은 프레임은 앞 목록의 것 하나만, 시간순."""
    seen = {}
    for frames in lists:
        for f in frames:
            seen.setdefault(f.frame_index, f)
    return sorted(seen.values(), key=lambda f: f.frame_index)


def keyframes(video: Path, select: list[str], change_det, text_det) -> None:
    print(f"\n=== [keyframe] {video.name}")
    reader = VideoReader(video)
    data = {"video": video.name, "fps": reader.fps, "duration": round(reader.duration, 3)}
    change_frames, text_frames = [], []

    if change_det:
        cands = candidates(reader, SAMPLE_INTERVAL)
        change_frames = change_det.select(reader, cands, CHANGE_THRESHOLD, MAX_KEYFRAMES)
        print(f"  visual change: {len(change_frames)} / {len(cands)} candidates")

    if text_det:
        spans = text_det.scan(reader, OCR_INTERVAL, OCR_SIM_MIN)
        print(f"  text spans: {len(spans)}")
        data["text_spans"] = [asdict(t) for t in spans]
        if "text" in select:
            text_frames = rep_frames(spans)

    if select:
        frames = merge_frames(change_frames, text_frames)
        for f in frames:
            path = FRAME_DIR / video.stem / f"{f.frame_index:06d}.jpg"
            reader.save(f.frame_index, path)
            f.path = str(path)
        data["frames"] = [asdict(f) for f in frames]

    reader.close()
    save(f"{video.stem}.keyframes.json", data)


def load_keyframes(video: Path) -> dict:
    path = OUTPUT_DIR / f"{video.stem}.keyframes.json"
    if not path.exists():
        sys.exit(f"키프레임 파일 없음: {path}  → 먼저 python main.py keyframes")
    return json.loads(path.read_text(encoding="utf-8"))


def text_claims(video: Path, extractor: TextClaimExtractor) -> None:
    spans = [{"span_id": i, "t_start": t["start"], "t_end": t["end"], "t_rep": t["t_rep"], "text": t["text"],
              "frame_index": t["frame_index"]}
             for i, t in enumerate(load_keyframes(video)["text_spans"])]
    print(f"\n=== [text] {video.name}  ({len(spans)} spans)")
    claims = extractor.extract(spans)
    print(f"  claims: {len(claims)}")
    for c in claims:
        print(f"    - {c['claim_id']} [{c['claim_type']}] {c['text']}  ({c['t_start']:.1f}~{c['t_end']:.1f}s)")
    save(f"{video.stem}.visual_text_claims.json",
         {"video_id": video.stem, "video": video.name, "screen_texts": spans, "claims": claims})


def scene_claims(video: Path, extractor: SceneClaimExtractor) -> None:
    kf = load_keyframes(video)
    spans = [{"span_id": i, "t_start": t["start"], "t_end": t["end"], "t_rep": t["t_rep"], "text": t["text"],
              "frame_index": t["frame_index"]}
             for i, t in enumerate(kf.get("text_spans", []))]
    print(f"\n=== [scene] {video.name}  ({len(kf['frames'])} frames)")
    claims = extractor.extract(kf["frames"], kf["duration"], spans)
    print(f"  claims: {len(claims)}")
    for c in claims:
        print(f"    - {c['claim_id']} [{c['claim_type']}] {c['text']}  ({c['t_start']:.1f}~{c['t_end']:.1f}s)")
    save(f"{video.stem}.visual_scene_claims.json",
         {"video_id": video.stem, "video": video.name, "frames": kf["frames"], "screen_texts": spans,
          "claims": claims})


def main():
    p = argparse.ArgumentParser(usage=__doc__)
    p.add_argument("stage", choices=["keyframes", "text", "scene"])
    p.add_argument("target", nargs="*", type=Path, default=[INPUT_PATH])
    p.add_argument("--select", default="text", help="keyframes: VLM 입력 프레임 선택기 (change,text). 빈 값이면 프레임 없음")
    p.add_argument("--ocr", action="store_true", help="keyframes: text 선택기 없이도 OCR 글자 구간 생성")
    args = p.parse_args()
    videos = [v for t in args.target for v in list_inputs(t)]
    if not videos:
        sys.exit(f"입력 영상이 없음: {args.target}")

    if args.stage == "keyframes":
        select = [s for s in args.select.split(",") if s]
        if not select and not args.ocr:
            sys.exit(f"선택기 없음: --select {args.select!r}, --ocr 없음")
        change_det = ChangeDetector(CHANGE_MODEL, SMALL_DEVICE, VJEPA_FRAMES) if "change" in select else None
        text_det = (TextDetector(OCR_MODEL, SMALL_DEVICE, batch=OCR_BATCH, max_pixels=OCR_MAX_PIXELS)
                    if "text" in select or args.ocr else None)
        for v in videos:
            keyframes(v, select, change_det, text_det)
    elif args.stage == "text":
        extractor = TextClaimExtractor(LLMClient(LLM_BASE_URL, LLM_MODEL))
        for v in videos:
            text_claims(v, extractor)
    else:
        extractor = SceneClaimExtractor(VLM(VLM_BASE_URL))
        for v in videos:
            scene_claims(v, extractor)


if __name__ == "__main__":
    main()
