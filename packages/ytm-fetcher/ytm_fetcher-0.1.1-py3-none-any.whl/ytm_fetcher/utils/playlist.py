from api.setup import api_fetcher
from formatting import format_tracklist, extract_ids
from models import Playlist

def fetch_playlist(pl_id):
    pl = api_fetcher.get_playlist(pl_id, limit=None)
    title, author = pl['title'], pl['author']
    songs = format_tracklist(pl['tracks'])

    return Playlist(pl_id, title, author, songs)

def create_ytm_playlist(pl):
    song_ids = extract_ids(pl.songs)
    playlist_id = api_fetcher.create_playlist(pl.name, pl.description, video_ids=song_ids)
    return playlist_id


