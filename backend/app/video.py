import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from .errors import ApiError

PATHS = {
    "youtube.com": (r"/shorts/[\w-]+/?",),
    "youtu.be": (r"/[\w-]+/?",),
    "instagram.com": (r"/reels?/[\w-]+/?", r"/p/[\w-]+/?"),
    "tiktok.com": (r"/@[\w.-]+/video/\d+/?",),
    "vm.tiktok.com": (r"/[\w-]+/?",),
    "vt.tiktok.com": (r"/[\w-]+/?",),
}

PHRASES = (
    # yt_dlp/extractor/common.py:1228, 1247
    "This video is only available for registered users",
    "This video is DRM protected",
    # yt_dlp/extractor/tiktok.py:290-292, 331-333, 1009-1012
    "TikTok is requiring login for access to this content",
    "This post may not be comfortable for some audiences",
    "You do not have permission to view this post",
    # yt_dlp/extractor/instagram.py:495-496, 502-503
    "Restricted Video",
    "This content is only available for registered users who follow this account",
    # yt_dlp/extractor/youtube/_video.py:2901 (연령 제한 판별)
    "Sign in to confirm your age",
    # YouTube playabilityStatus 텍스트 (yt_dlp/extractor/youtube/_video.py:198, 818, 902 테스트 fixture)
    "Private video",
    "Video unavailable",
    "This video has been removed",
    # 실측(2026-11-15 live probe): 없는 영상 id
    "This video is unavailable",
)

TRANSIENT = (
    # yt_dlp/extractor/youtube/_video.py:4068, 4072
    "requiring a captcha challenge",
    "has been rate-limited",
)


def check_url(url: str) -> None:
    try:
        parts = urlsplit(url)
    except ValueError:
        raise ApiError("URL_001") from None
    host = re.sub(r"^(www|m)\.", "", parts.hostname or "")
    watch = host == "youtube.com" and parts.path == "/watch" and parse_qs(parts.query).get("v")
    if parts.scheme not in ("http", "https") or not (
            watch or any(re.fullmatch(p, parts.path) for p in PATHS.get(host, ()))):
        raise ApiError("URL_001")


def probe(url: str) -> tuple[str, str | None, float | None]:
    with YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except DownloadError as e:
            known = any(p in e.msg for p in PHRASES) and not any(m in e.msg for m in TRANSIENT)
            raise ApiError("URL_002" if known else "JOB_001") from None
        except Exception:
            raise ApiError("JOB_001") from None
    if (info.get("_type") in ("playlist", "multi_video") or info.get("is_live") or info.get("_has_drm")
            or info.get("availability") in ("private", "premium_only", "subscriber_only", "needs_auth")):
        raise ApiError("URL_002")
    duration = info.get("duration")
    return info["id"], info.get("title"), None if duration is None else float(duration)


def download(url: str, run_dir: Path, video_id: str) -> Path:
    opts = {"quiet": True, "noplaylist": True,
            "outtmpl": str(run_dir / f"{video_id}.%(ext)s"),
            "format": "bestvideo+bestaudio/best", "merge_output_format": "mp4",
            "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]}
    with YoutubeDL(opts) as ydl:
        ydl.download([url])
    path = run_dir / f"{video_id}.mp4"
    if not path.exists():
        raise FileNotFoundError(path)
    return path
