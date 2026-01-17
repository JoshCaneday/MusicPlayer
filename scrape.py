import shutil
import subprocess
import sys
import os

class Scraper:
    def __init__(self):
        self.JS_RUNTIME = "node"
        self.AUDIO_DIR = "./music"
        if not os.path.exists(self.AUDIO_DIR):
            os.makedirs(self.AUDIO_DIR)

        self.yt_dlp = shutil.which("yt-dlp")
        if self.yt_dlp is None:
            print("ERROR: yt-dlp not found on PATH.", file=sys.stderr)

    def get(self, url, folder, playlist_items=None):
        target_dir = os.path.join(self.AUDIO_DIR, folder)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        cmd = [
            self.yt_dlp,
            "--js-runtimes", self.JS_RUNTIME,
            "--cookies", "cookies.txt",
            "--extract-audio",
            "--audio-format", "wav",
            "--audio-quality", "0",
            "--sleep-interval", "10",
            "--max-sleep-interval", "30",
            "--no-playlist" if not playlist_items else "--yes-playlist",
            "-P", target_dir,
        ]

        if playlist_items:
            cmd.extend(["--playlist-items", playlist_items])

        cmd.append(url)

        try:
            rc = subprocess.call(cmd)
            return rc == 0
        except Exception as e:
            print(f"Download Error: {e}")
            return False