"""python main.py keyframes|claims [영상.mp4 | 폴더]   # 1단계: 키프레임 선별 / 2단계: VLM Claim 추출 (serve_vlm.sh 서버 필요)"""
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from claim_extraction.visual.claim import VLM, VisualClaimExtractor         # noqa: E402
from claim_extraction.visual.keyframe import (ChangeDetector, Keyframe,     # noqa: E402
                                              ShotDetector, TextDetector, VideoReader,
                                              aggregate, list_inputs, shot_candidates)

# ── 입출력 ─────────────────────────────────────────────
INPUT_PATH = ROOT / "data"
OUTPUT_DIR = ROOT / "data" / "output"
FRAME_DIR = ROOT / "data" / "frames"        # 선택된 프레임 이미지

# ── Keyframe Selection ─────────────────────────────────
SHOT_MODEL_DEVICE = "cuda:0"
CHANGE_MODEL = "facebook/vjepa2-vitg-fpc64-384"
OCR_MODEL = "PaddlePaddle/PaddleOCR-VL-1.6"
SMALL_DEVICE = "cuda:0"                     # V-JEPA 2, OCR, TransNetV2 올릴 카드

SAMPLE_INTERVAL = 0.5                       # 샷 안에서 후보 프레임 간격(초)
PER_SHOT_MAX = 6                            # 샷당 후보 상한
CHANGE_THRESHOLD = 0.10                     # 1 - cosine. 이 이상 달라야 새 프레임
OCR_INTERVAL = 0.5                          # 원본 전체 OCR 간격(초)
MAX_KEYFRAMES = 25                          # 최종 프레임 상한

# ── Visual Claim Extraction (llama-server, serve_vlm.sh로 띄움) ──
VLM_BASE_URL = os.environ.get("VLM_BASE_URL", "http://localhost:8002/v1")


def select_keyframes(video: Path, shot_det, change_det, text_det) -> list[Keyframe]:
    print(f"\n=== [keyframe] {video.name}")
    reader = VideoReader(video)

    shots = shot_det.detect(video)
    print(f"  shots: {len(shots)}")

    candidates = shot_candidates(reader, shots, SAMPLE_INTERVAL, PER_SHOT_MAX)
    change = change_det.select(reader, candidates, CHANGE_THRESHOLD)
    print(f"  visual change: {len(change)} / {len(candidates)} candidates")

    texts = text_det.scan(reader, OCR_INTERVAL)
    print(f"  text spans: {len(texts)}")

    keyframes = aggregate(reader, shots, change, texts, MAX_KEYFRAMES)
    for kf in keyframes:
        path = FRAME_DIR / video.stem / f"{kf.frame_index:06d}.jpg"
        reader.save(kf.frame_index, path)
        kf.path = str(path)
    reader.close()
    print(f"  keyframes: {len(keyframes)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / f"{video.stem}.keyframes.json"
    out.write_text(json.dumps({
        "video": video.name,
        "fps": reader.fps,
        "shots": [asdict(s) for s in shots],
        "text_spans": [asdict(t) for t in texts],
        "keyframes": [asdict(k) for k in keyframes],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  saved: {out.relative_to(ROOT)}")
    return keyframes


def _load_keyframe_file(video: Path) -> dict:
    path = OUTPUT_DIR / f"{video.stem}.keyframes.json"
    if not path.exists():
        sys.exit(f"키프레임 파일 없음: {path}  → 먼저 python main.py keyframes")
    return json.loads(path.read_text(encoding="utf-8"))


def load_keyframes(video: Path) -> list[Keyframe]:
    return [Keyframe(**k) for k in _load_keyframe_file(video)["keyframes"]]


def load_screen_texts(video: Path) -> list[dict]:
    # 화면 글자 노출 구간. Alignment 단계에서 Conflict·target 해소 참고용
    return [
        {"text": t["text"], "t_start": t["start"], "t_end": t["end"], "frame_index": t["frame_index"]}
        for t in _load_keyframe_file(video)["text_spans"]
    ]


def extract_claims(video: Path, keyframes: list[Keyframe], extractor) -> Path:
    print(f"\n=== [claim] {video.name}  ({len(keyframes)} frames)")
    claims = extractor.extract(keyframes)
    print(f"  claims: {len(claims)}")
    for c in claims:
        print(f"    - {c.claim_id} [{'/'.join(c.types) or '-'}] {c.text}  ({c.timestamp:.1f}s, {c.scope})")

    out = OUTPUT_DIR / f"{video.stem}.visual_claims.json"
    out.write_text(json.dumps({
        "video_id": video.stem,
        "video": video.name,
        "screen_texts": load_screen_texts(video),
        "keyframes": [asdict(k) for k in keyframes],
        "claims": [asdict(c) for c in claims],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  saved: {out.relative_to(ROOT)}")
    return out


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("keyframes", "claims"):
        sys.exit(__doc__)
    stage = sys.argv[1]
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else INPUT_PATH
    videos = list_inputs(target)
    if not videos:
        sys.exit(f"입력 영상이 없음: {target}")

    if stage == "keyframes":
        shot_det = ShotDetector(SHOT_MODEL_DEVICE)
        change_det = ChangeDetector(CHANGE_MODEL, SMALL_DEVICE)
        text_det = TextDetector(OCR_MODEL, SMALL_DEVICE)
        for v in videos:
            select_keyframes(v, shot_det, change_det, text_det)
    else:
        extractor = VisualClaimExtractor(VLM(VLM_BASE_URL))
        for v in videos:
            extract_claims(v, load_keyframes(v), extractor)


if __name__ == "__main__":
    main()
