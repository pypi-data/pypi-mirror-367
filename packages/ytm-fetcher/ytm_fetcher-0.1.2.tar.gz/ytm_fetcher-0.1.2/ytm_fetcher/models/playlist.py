class Playlist:
    """ A class to represent a playlist containing a list of songs. """
    def __init__(self, songs=None, name=None, description=None, playlist_id=-1):
        """
        Initializes a Playlist object with the provided details.

        :param list[Song] songs: A list of Song objects comprising the playlist
        :param str name: Playlist name. Required for YTM playlists.
        :param str description: Playlist description. Required for YTM playlists.
        :param str playlist_id: A unique identifier for the playlist.
        Defaults to -1 to indicate that the playlist is not on YTM.
        Not intended to be modified or defined by the user directly.
        """

        # Setting default values for variables
        if songs is None:
            songs = []

        if name is None:
            name = 'Playlist'

        if description is None:
            description = ''

        self.songs = songs
        self.name = name
        self.description = description
        self.playlist_id = playlist_id

    def __len__(self):
        """
        Returns the total length of the playlist, in seconds
        :return: Length of the playlist, in seconds.
        :rtype: int
        """
        return sum(list(map(lambda x: x.duration, self.songs)))

    def __repr__(self, pp=False):
        """
        Returns a string representation of the Playlist object.

        :return: A string representation of the Playlist object.
        :rtype: str
        """
        fill = '\n\t' if pp else ''
        fill2 = '\n' if pp else ''
        fill3 = '' if pp else ' '
        return f"Playlist({fill}id={self.playlist_id},{fill}{fill3}name='{self.name}'," \
               f"{fill}{fill3}duration_sec={len(self)},{fill}{fill3}song_count={len(self.songs)}{fill2})"

    def __str__(self, pp=False):
        return self.__repr__(pp)

    def add_song(self, song):
        """
        Adds a song to the playlist.

        :param Song song: The Song object to add to the playlist.
        """
        self.songs.append(song)

    def extend_songs(self, songs):
        """
        Extends the playlist with a list of songs.
        :param list[Song] songs: A list of Song objects to add to the playlist.
        """
        self.songs.extend(songs)

    def remove_song(self, song_id):
        """
        Removes a song from the playlist by its ID.

        :param str song_id: The ID of the song to remove.
        :return: True if the song was removed, False otherwise.
        :rtype: bool
        """
        for song in self.songs:
            if song.id == song_id:
                self.songs.remove(song)
                return True
        return False

    def merge(self, *playlists, static=False):
        """
        Depending on flag, either merges other playlists into this one
        or creates a new playlist with the combined tracks of its constituents.
        :param bool static: If true, behavior mirrors that expected of a static function
        If false, other playlists are merged into this one.
        :param *Playlist playlists: Playlists to combine
        """
        #
        all_songs = self.songs

        for other in playlists:
            if static:
                all_songs.extend(other.songs)
            else:
                self.songs.extend(other.songs)

        if static:
            return Playlist(all_songs)

        return None
