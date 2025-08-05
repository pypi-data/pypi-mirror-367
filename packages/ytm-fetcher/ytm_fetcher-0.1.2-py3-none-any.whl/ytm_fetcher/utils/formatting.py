from ..models import Song
import re

def format_tracklist(tracks):
    songs = []
    for track in tracks:
        s = Song(
            track['videoId'],
            track.get('title', 'Unknown Title'),
            track['artists'][0]['name'],
            track.get('duration_seconds', 0)
        )
        songs.append(s)
    return songs

def extract_ids(tracks):
    """
    :param tracks: Accepts either a list of Song objects or a list of dictionaries with videoId keys
    :return: Returns a list of YouTube Music song IDs
    """
    if len(tracks) == 0:
        return []
    if isinstance(tracks[0], Song):
        return list(map(lambda x: x.id, tracks))
    else:
        return list(map(lambda x: x['videoId'], tracks))


def clean_title(title):
    """
    Ensures the title of a song is valid for writing to file
    by replacing illegal characters with %.
    :param str title: Prospective filename.
    :return: Title guaranteed to be valid for writing to file.
    :rtype: str
    """

    # Substitute all illegal characters with #
    title = re.sub(r'[<|:>/\\*?]', '%', title)

    # Double quotes also disallowed on Windows
    title = re.sub('"', "'", title)
    return title

