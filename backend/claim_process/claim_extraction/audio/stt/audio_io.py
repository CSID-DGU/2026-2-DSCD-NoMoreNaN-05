import subprocess
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4a", ".mp3", ".wav"}


def list_inputs(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.iterdir() if p.suffix.lower() in VIDEO_EXTS)


def extract_wav(video: Path, out_dir: Path, sr: int = 16000) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    wav = out_dir / f"{video.stem}.wav"
    if wav.exists() and wav.stat().st_mtime >= video.stat().st_mtime:
        return wav
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-vn", "-ac", "1", "-ar", str(sr), str(wav)],
        check=True,
    )
    return wav
