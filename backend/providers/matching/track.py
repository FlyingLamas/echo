class UniversalTrack:
    def __init__(
        self,
        title: str,
        artists: list[str],
        album: str | None = None,
        isrc: str | None = None,
        duration_ms: int | None = None,
    ):
        self.title = title
        self.artists = artists
        self.album = album
        self.isrc = isrc
        self.duration_ms = duration_ms

    def primary_artist(self):
        return self.artists[0] if self.artists else ""