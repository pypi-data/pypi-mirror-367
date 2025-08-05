import os
import sys

import yt_dlp
import ytmusicapi as ytm

CODEC = 'wav'


# Making sure relative paths are correct
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
AUTH_DIR = os.path.join(PROJECT_ROOT, "auth")

print(f'Searching for auth files at "{AUTH_DIR}"', file=sys.stderr)

# Setting auth paths
cookie_txt = os.path.join(AUTH_DIR, "cookies.txt")
header_txt = os.path.join(AUTH_DIR, "headers.txt")
header_json = os.path.join(AUTH_DIR, "headers.json")

if not os.path.exists(cookie_txt):
    print("No cookie file found, aborting...", file=sys.stderr)
    exit(1)
print('Found cookie.txt...', file=sys.stderr)

if not (os.path.exists(header_txt) or os.path.exists(header_json)):
    print("No header file found, aborting...", file=sys.stderr)
    exit(1)
print('Found browser header data...', file=sys.stderr)


# Needed to format downloaded files
ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"

if not os.path.exists(ffmpeg_path):
    print("No ffmpeg executable found, aborting...", file=sys.stderr)
    exit(1)
print('Found ffmpeg executable...', file=sys.stderr)

# Setting up yt-dlp object
dl_options = {
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': CODEC,
        'preferredquality': '192',
    }],
    'cookiefile': cookie_txt,
    'ffmpeg_location': ffmpeg_path
}
downloader = yt_dlp.YoutubeDL(dl_options)

# Formatting header json
if not os.path.exists(header_json):
    print("No header JSON found. Creating new one...", file=sys.stderr)
    with open(header_txt) as hf:
        headers = hf.read()
    ytm.setup(filepath=header_json, headers_raw=headers)

# Creating ytm api object
api_fetcher = ytm.YTMusic(header_json)

# Throws an error if auth problems
try:
    ls = api_fetcher.get_liked_songs()
    print("Authentication successful", file=sys.stderr)
except Exception:
    print("Authentication Error, aborting...", file=sys.stderr)
    exit(1)