"""Accept bare video URLs, save MP4s to the Windows Desktop, and open them."""

import ctypes
from ctypes import wintypes
import os
from pathlib import Path

import download_video as downloader


def desktop_directory():
    buffer = ctypes.create_unicode_buffer(32768)
    # CSIDL_DESKTOPDIRECTORY resolves the actual Desktop, including redirected folders.
    function = ctypes.windll.shell32.SHGetFolderPathW
    function.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR]
    function.restype = ctypes.c_long
    if function(None, 0x10, None, 0, buffer) != 0:
        raise RuntimeError("Could not locate the Windows Desktop.")
    return Path(buffer.value)


def main():
    downloader.VIDEO_DIR = desktop_directory()
    print("Video URL mode: paste a URL and press Enter. Type exit to quit.")
    while True:
        try:
            url = input("URL > ").strip()
            if url.lower() == "exit":
                break
            if not url:
                continue
            saved = downloader.download_video(url)
            print(f"Saved: {saved}")
            os.startfile(str(saved))
        except (EOFError, KeyboardInterrupt):
            print("\nStopped.")
            break
        except Exception as exc:
            print(f"Failed: {exc}")


if __name__ == "__main__":
    main()
