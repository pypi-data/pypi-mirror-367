import os
import subprocess
import sys

from playsound import playsound
from ..models import Song
from ..api import ffmpeg_path

def play(song_or_path, song_dir=None):
    if isinstance(song_or_path, Song):
        if not song_dir:
            song_dir = os.getcwd()
        path = song_dir + song_or_path.title + '.wav'
    else:
        path = song_or_path

    try:
        playsound(path)
    except Exception as e:
        print(f"Problem playing song: {e}, aborting...", file=sys.stderr)
        exit(1)


def sample(song_or_path, seconds=15, song_dir=None):
    if isinstance(song_or_path, Song):
        if not song_dir:
            song_dir = os.getcwd()
        path = song_dir + song_or_path.title + '.wav'
    else:
        path = song_or_path

    try:
        sample_path = f"{path[:-4]}_temp.wav"
        command = [
            ffmpeg_path,
            '-y',
            "-loglevel", "quiet",
            "-i", song_or_path,
            "-ss", str(0),
            "-to", str(15),
            "-c", "copy",  # Copy codec without re-encoding
            sample_path
        ]
        subprocess.run(command)
        playsound(sample_path)
        os.remove(sample_path)

    except Exception as e:
        print(f"Problem playing song: {e}, aborting...", file=sys.stderr)
        exit(1)


