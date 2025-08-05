class Song:
    """
    A class to represent a song with its details.

    Attributes:
        id (str): The unique identifier for the song.
        title (str): The title of the song.
        artist (str): The artist of the song.
        duration (int): The duration of the song in seconds.
    """

    def __init__(self, id, title, artist, duration):
        """
        Initializes a Song object with the provided details.

        :param str id: The unique identifier for the song.
        :param str title: The title of the song.
        :param str artist: The artist of the song.
        :param int duration: The duration of the song in seconds.
        """
        self.id = id
        self.title = title
        self.artist = artist
        self.duration = duration

    def __repr__(self, pp=False):
        """
        Returns a string representation of the Song object.

        :return: A string representation of the Song object.
        :rtype: str
        """
        fill = '\n\t' if pp else ''
        fill2 = '\n' if pp else ''
        fill3 = '' if pp else ' '
        return f"Song({fill}id={self.id},{fill}{fill3}title='{self.title}'," \
               f"{fill}{fill3}artist='{self.artist}',{fill}{fill3}" \
               f"duration_secs={self.duration}{fill2})"

    def __str__(self, pp=False):
        return self.__repr__(pp)