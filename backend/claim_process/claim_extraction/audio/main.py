import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from claim_process.claim_extraction.audio.claim import ClaimExtractor                     # noqa: E402
from claim_process.claim_extraction.audio.stt import (CharTimeline, Transcriber,         # noqa: E402
                                        extract_wav, list_inputs, split_sentences)
from claim_process.claim_extraction.common import LLMClient                              # noqa: E402

# ── 입출력 ─────────────────────────────────────────────
INPUT_PATH = ROOT / "data"              # mp4 파일 하나 또는 폴더
OUTPUT_DIR = ROOT / "data" / "output"
WAV_DIR = ROOT / "data" / "wav"         # ffmpeg로 뽑은 오디오 캐시
LANGUAGE = "Korean"

# ── STT ────────────────────────────────────────────────
STT_MODEL = "Qwen/Qwen3-ASR-1.7B"       # 모델
ALIGNER_MODEL = "Qwen/Qwen3-ForcedAligner-0.6B"   # 모델
DEVICE = "cuda:0"

# ── Claim 추출 LLM (llama-server, serve_llm.sh로 띄움) ──
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-oss-120b")


def ocr_context(video: Path) -> str:
    """이번 실행의 keyframes.json 화면 글자 구간 text(같은 글자는 한 번)를 줄바꿈으로 잇는다."""
    spans = json.loads((OUTPUT_DIR / f"{video.stem}.keyframes.json").read_text(encoding="utf-8"))["text_spans"]
    return "\n".join(dict.fromkeys(s["text"] for s in spans))


def run(video: Path, stt: Transcriber, extractor: ClaimExtractor, use_ocr: bool) -> Path:
    print(f"\n=== {video.name}")
    wav = extract_wav(video, WAV_DIR)

    context = ocr_context(video) if use_ocr else ""
    print(f"  ASR context: {len(context)} chars")
    text, words = stt.transcribe(wav, LANGUAGE, context)
    print(f"  STT: {len(words)} words / {len(text)} chars")

    tl = CharTimeline(text, words)
    segments = split_sentences(tl)
    print(f"  segments: {len(segments)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    transcript_out = OUTPUT_DIR / f"{video.stem}.transcript.json"
    transcript_out.write_text(
        json.dumps(
            {
                "video": video.name,
                "language": LANGUAGE,
                "asr_context": context,
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

    claims = extractor.extract(segments, tl)
    print(f"  claims: {len(claims)}")
    for c in claims:
        print(f"    - {c['claim_id']} [{c['claim_type']}] {c['text']}  ({c['t_start']:.1f}~{c['t_end']:.1f}s)")

    out = OUTPUT_DIR / f"{video.stem}.audio_claims.json"
    out.write_text(
        json.dumps(
            {
                "video_id": video.stem,
                "video": video.name,
                "language": LANGUAGE,
                "transcript": [
                    {"segment_id": s.id, "t_start": s.start, "t_end": s.end, "text": s.text}
                    for s in segments
                ],
                "claims": claims,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  saved: {out.relative_to(ROOT)}")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("target", nargs="*", type=Path, default=[INPUT_PATH], help="영상 파일·폴더 여러 개")
    p.add_argument("--ocr-context", action="store_true", help="keyframes.json 화면 글자를 ASR context로")
    args = p.parse_args()
    videos = [v for t in args.target for v in list_inputs(t)]
    if not videos:
        sys.exit(f"입력 영상이 없음: {args.target}")

    stt = Transcriber(STT_MODEL, ALIGNER_MODEL, DEVICE)
    extractor = ClaimExtractor(LLMClient(LLM_BASE_URL, LLM_MODEL))

    for v in videos:
        run(v, stt, extractor, args.ocr_context)


if __name__ == "__main__":
    main()
