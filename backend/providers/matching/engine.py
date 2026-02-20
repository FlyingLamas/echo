from rapidfuzz import fuzz
from .normalizer import normalize_text
from .track import UniversalTrack


TITLE_THRESHOLD = 85
ARTIST_THRESHOLD = 80


def is_match(source: UniversalTrack, candidate: UniversalTrack) -> bool:
    # ISRC direct match (best case)
    if source.isrc and candidate.isrc:
        if source.isrc == candidate.isrc:
            return True

    # Normalize
    source_title = normalize_text(source.title)
    candidate_title = normalize_text(candidate.title)

    source_artist = normalize_text(source.primary_artist())
    candidate_artist = normalize_text(candidate.primary_artist())

    title_score = fuzz.ratio(source_title, candidate_title)
    artist_score = fuzz.ratio(source_artist, candidate_artist)

    return (
        title_score >= TITLE_THRESHOLD and
        artist_score >= ARTIST_THRESHOLD
    )
    