from api import api_fetcher
from formatting import format_tracklist
from models import Song
import re



def search_songs(query):
    """
    Searches for songs based on the provided query.

    :param str query: The search query.
    :return: A list of Song objects representing the search results.
    :rtype: list[Song]
    """
    results = api_fetcher.search(query, filter='songs')
    songs = format_tracklist(results)
    return songs

def fetch_song(song_id):
    song = api_fetcher.get_song(song_id)
    return Song(song_id, song['title'], song['artists'][0]['name'], song['duration_seconds'])