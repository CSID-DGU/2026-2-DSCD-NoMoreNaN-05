"""Download one anonymously accessible video to the project's MP4 directory."""

import argparse
import hashlib
from pathlib import Path
import shutil
import sys
from urllib.parse import urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIDEO_DIR = PROJECT_ROOT / "data" / "raw" / "ads" / "videos"


def download_video(url: str) -> Path:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS video URL.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing authentication credentials are not supported.")

    try:
        from yt_dlp import YoutubeDL
    except ImportError as exc:
        raise RuntimeError(
            "yt-dlp is missing. Run: python -m pip install -r requirements.txt"
        ) from exc

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        ffmpeg_path = next(
            (str(path) for path in (PROJECT_ROOT / ".tools").glob("ffmpeg*/bin/ffmpeg.exe")),
            None,
        )
    has_ffmpeg = ffmpeg_path is not None

    def check_video(info, *, incomplete=False):
        if info.get("is_live"):
            return "Live streams are not supported; use a completed video."
        if info.get("has_drm"):
            return "DRM-protected videos are not supported."
        if info.get("availability") in {"private", "premium_only", "subscriber_only", "needs_auth"}:
            return "This video requires authentication or a subscription."
        return None

    options = {
        "outtmpl": str(VIDEO_DIR / "%(id)s.%(ext)s"),
        "windowsfilenames": True,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 2,
        "fragment_retries": 2,
        "geo_bypass": False,
        "allow_unplayable_formats": False,
        "match_filter": check_video,
        # Prefer a combined MP4. Separate streams / other containers need FFmpeg.
        "format": "best[ext=mp4]/bestvideo+bestaudio/best" if has_ffmpeg else "best[ext=mp4]",
        "merge_output_format": "mp4",
    }
    # CDN URLs have no post ID; generic extraction may treat the whole query
    # string as an ID (too long for Windows). Name by the stable media path.
    is_tiktok_cdn = parsed.hostname.lower().endswith(".tiktokcdn.com")
    if is_tiktok_cdn:
        media_key = hashlib.sha256(parsed.path.rstrip("/").rsplit("/", 1)[-1].encode()).hexdigest()[:24]
        options["outtmpl"] = str(VIDEO_DIR / f"tiktok_{media_key}.%(ext)s")
    if has_ffmpeg:
        options["ffmpeg_location"] = str(Path(ffmpeg_path).parent)
        options["postprocessors"] = [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
        ]
    deno_path = shutil.which("deno")
    local_deno = PROJECT_ROOT / ".tools" / "deno" / "deno.exe"
    if not deno_path and local_deno.is_file():
        deno_path = str(local_deno)
    if deno_path:
        options["js_runtimes"] = {"deno": {"path": deno_path}}

    with YoutubeDL(options) as downloader:
        # Inspect before downloading so playlist-only URLs never download a batch.
        info = downloader.extract_info(url, download=False)
        if not info:
            raise RuntimeError("No downloadable public video was found.")
        if info.get("_type") in {"playlist", "multi_video"} or "entries" in info:
            raise ValueError("Enter a single video URL, not a playlist or multi-video post.")
        rejection = check_video(info)
        if rejection:
            raise RuntimeError(rejection)
        result = downloader.process_ie_result(info, download=True)
        if not result:
            raise RuntimeError("The video was not downloaded.")
        saved_path = Path(downloader.prepare_filename(result)).with_suffix(".mp4")

    if not saved_path.is_file() or saved_path.stat().st_size == 0:
        raise RuntimeError("Download finished without a non-empty MP4 file.")
    return saved_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Public video URL (HTTP/HTTPS)")
    args = parser.parse_args()
    try:
        saved_path = download_video(args.url.strip())
    except KeyboardInterrupt:
        print("Download failed\nReason: Download cancelled.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Download failed\nReason: {exc}", file=sys.stderr)
        if shutil.which("ffmpeg") is None and not any(
            (PROJECT_ROOT / ".tools").glob("ffmpeg*/bin/ffmpeg.exe")
        ):
            print("Hint: Install FFmpeg and add it to PATH if MP4 merging/conversion is needed.", file=sys.stderr)
        return 1
    print(f"Download successful\nSaved to: {saved_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
