import re


def filter_tracklist(tracks):
    filter_words = ['live', 'extended', 'edition', 'dub', 'radio', 'edit', 'mix', 'version']
    filter_rgx = re.compile('|'.join(filter_words), flags=re.IGNORECASE)
    tracks_filtered = []

    for song in tracks:
        if not filter_rgx.search(song.title):
            tracks_filtered.append(song)

    return tracks_filtered


def choose_track(tracks):
    filtered = filter_tracklist(tracks)
    if filtered:
        return filtered[0]
    else:
        return tracks[0]


def parse_playlist_link(link):
    match = re.match(".*list=([^&]+).*", link)
    if match:
        return match.group(1)

    return None
