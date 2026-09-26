import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from claim import ClaimExtractor, LLMClient
from stt import Transcriber, extract_wav, list_inputs, segment_words

ROOT = Path(__file__).resolve().parents[2]

# ── 입출력 ─────────────────────────────────────────────
INPUT_PATH = ROOT / "data"              # mp4 파일 하나 또는 폴더
OUTPUT_DIR = ROOT / "data" / "output"
WAV_DIR = ROOT / "data" / "wav"         # ffmpeg로 뽑은 오디오 캐시
LANGUAGE = "Korean"

# ── STT ────────────────────────────────────────────────
STT_MODEL = "Qwen/Qwen3-ASR-1.7B"       # 모델
ALIGNER_MODEL = "Qwen/Qwen3-ForcedAligner-0.6B"   # 모델
DEVICE = "cuda:0"

# ── Claim 추출 LLM (vLLM OpenAI 호환 서버) ──────────────
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")


def run(video: Path, stt: Transcriber, extractor: ClaimExtractor) -> Path:
    print(f"\n=== {video.name}")
    wav = extract_wav(video, WAV_DIR)

    text, words = stt.transcribe(wav, LANGUAGE)
    print(f"  STT: {len(words)} words / {len(text)} chars")

    segments = segment_words(text, words)
    print(f"  segments: {len(segments)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transcript_out = OUTPUT_DIR / f"{video.stem}.transcript.json"
    transcript_out.write_text(
        json.dumps(
            {
                "video": video.name,
                "language": LANGUAGE,
                "transcript": text,
                "words": [asdict(w) for w in words],
                "segments": [asdict(s) for s in segments],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  saved: {transcript_out.relative_to(ROOT)}")

    claims = extractor.extract(segments)
    print(f"  claims: {len(claims)}")
    for c in claims:
        print(f"    - [{'/'.join(c.types)}] {c.claim}  ({c.start:.1f}~{c.end:.1f}s)")

    out = OUTPUT_DIR / f"{video.stem}.audio_claims.json"
    out.write_text(
        json.dumps(
            {
                "video": video.name,
                "language": LANGUAGE,
                "transcript": text,
                "segments": [asdict(s) for s in segments],
                "claims": [asdict(c) for c in claims],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  saved: {out.relative_to(ROOT)}")
    return out


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_PATH
    videos = list_inputs(target)
    if not videos:
        sys.exit(f"입력 영상이 없음: {target}")

    stt = Transcriber(STT_MODEL, ALIGNER_MODEL, DEVICE)
    extractor = ClaimExtractor(LLMClient(LLM_BASE_URL, LLM_MODEL))

    for v in videos:
        run(v, stt, extractor)


if __name__ == "__main__":
    main()
