import sys
import warnings
import os

from api import downloader
from models import Song, Playlist

from utils.song import fetch_song
from utils.formatting import clean_title
from utils.playlist import fetch_playlist
from utils.data import parse_playlist_link

def dl_song(song=None, song_id=None, title=None, write_dir=None, noisy=False):
    """
    Downloads a song with the given ID to the specified directory.

    :param noisy: Will log progress to stderr if selected.
    :param song: Song object to download.
    :param str write_dir: The directory to which the song will be saved.
    :param str title: The title of the song / resulting path root
    :param str song_id: The ID of the song.
    """

    # Checks to make sure there is exactly one downloadable id
    if not (isinstance(song, Song) ^ isinstance(song_id, str)):
        raise ValueError("Exactly one of Song object or ID must be provided.")

    # Define song based on ID
    if not isinstance(song, Song):
        song = fetch_song(song_id)

    # Parameter-defined title takes priority
    title = title if title else song.title

    # Removes invalid filepath characters from title
    title = clean_title(title)

    # Defaults to the current working directory
    if not write_dir:
        write_dir = os.getcwd()

    # Do not download if an audio file exists at the destination
    if os.path.exists(os.path.join(write_dir, f"{title}.wav")):
        warnings.warn(f"File already exists, skipping download: {title}.wav")
        return -1

    # Make the API request to download the file
    downloader.params["outtmpl"] = {'default': os.path.join(write_dir, title)}
    if noisy:
        downloader.params["quiet"] = False
    else:
        downloader.params["quiet"] = True

    downloader.download([song_id])

    if noisy:
        print(f"Downloaded {title}.wav", file=sys.stderr)
    return 1


def dl_playlist(playlist=None, playlist_id=None, write_dir=None, noisy=False):
    """
    Downloads all songs from a playlist to the specified directory.

    :param noisy:
    :param write_dir:
    :param playlist:
    :param str playlist_id: The YTM ID of the playlist to download.
    """
    if not os.path.exists(write_dir):
        os.makedirs(write_dir)

    # Checks to make sure there is exactly one downloadable id
    if not (isinstance(playlist, Playlist) ^ isinstance(playlist_id, str)):
        raise ValueError("Exactly one of Playlist object or ID must be provided.")

    write_dir = write_dir if write_dir else os.getcwd()

    # Define the playlist object from ID if none is provided
    if isinstance(playlist_id, str):
        parsed = parse_playlist_link(playlist)
        playlist_id = parsed if parsed else playlist_id
        playlist = fetch_playlist(playlist_id)

    for track in playlist.songs:
        try:
            dl_song(track, write_dir=write_dir, noisy=noisy)
        except Exception as e:
            if noisy:
                print(f"Problem downloading '{track.title}': {e}, continuing...", file=sys.stderr)

    return 1