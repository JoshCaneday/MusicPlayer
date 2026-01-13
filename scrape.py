import shutil
import subprocess
import sys

# Terminal Command Equivalent:
# yt-dlp --js-runtimes node -S "ext:mp4:m4a,vcodec:h264,acodec:aac" -P "./videos"  --merge-output-format mp4 "https://www.youtube.com/watch?v=4x7mxKG-9KI"

class Scraper:
    def __init__(self):
        self.JS_RUNTIME = "node"
        self.AUDIO_DIR = "./music"

        self.yt_dlp = shutil.which("yt-dlp")
        if self.yt_dlp is None:
            print("ERROR: yt-dlp not found on PATH.", file=sys.stderr)
            sys.exit(1)

    def get(self, url, folder):
        cmd = [
            self.yt_dlp,
            "--js-runtimes", self.JS_RUNTIME,
            "--cookies", "cookies.txt",  # Add this
            "--extract-audio",
            "--audio-format", "wav",
            "--audio-quality", "0",
            #"--sleep-interval", "20",
            #"--max-sleep-interval", "40",
            "--fragment-retries", "infinite", # Retries video segments indefinitely
            "-P", self.AUDIO_DIR + "/" + folder,
            url,
        ]
        try:
            rc = subprocess.call(cmd)
            return rc == 0
        except Exception as e:
            print(f"Download failed: {e}")
            return False
