from celery import shared_task
from providers.models import ProviderAccount
from providers.services.spotify_service import SpotifyService
from .matching.track import UniversalTrack
from .matching.engine import get_match_score


@shared_task(bind=True, max_retries=5)
def transfer_playlist_task(self, user_id, source_playlist_id, target_provider):
    try:
        #Get Provider Account (Spotify for MVP)
        source_account = ProviderAccount.objects.get(user_id=user_id,provider__name="spotify")
        source_service = SpotifyService(source_account)
        target_service = SpotifyService(source_account)  # Spotify→Spotify

        # Fetch Source Tracks
        if source_playlist_id == "liked_songs":
            source_tracks = source_service.get_liked_songs()
            playlist_name = "Liked Songs Transfer"
        else:
            source_tracks = source_service.get_playlist_tracks(source_playlist_id)
            playlist_name = "Transferred Playlist"

        # Convert to UniversalTrack
        universal_tracks = []

        for track in source_tracks:
            universal_tracks.append(
                UniversalTrack(
                    title=track["name"],
                    artists=track["artists"],
                    album=track.get("album"),
                    isrc=track.get("external_ids", {}).get("isrc"),
                    duration_ms=track.get("duration_ms"),
                )
            )

        matched_uris = []
        unmatched = 0

        # Matching Loop
        for source_track in universal_tracks:

            query = f"{source_track.title} {source_track.primary_artist()}".strip()
            # We are adding following if condition, if title or promary artist is empty then q="" becomes empty, and it will return 400 no search query
            if not query:
                unmatched += 1
                continue
            
            candidates = target_service.search_track(query)

            best_score = 0
            best_uri = None

            for candidate in candidates:

                candidate_track = UniversalTrack(
                    title=candidate["name"],
                    artists=[a["name"] for a in candidate["artists"]],
                    album=candidate["album"]["name"],
                    isrc=candidate.get("external_ids", {}).get("isrc"),
                    duration_ms=candidate.get("duration_ms")
                )

                score = get_match_score(source_track, candidate_track)

                if score > best_score:
                    best_score = score
                    best_uri = candidate["uri"]
                
                if best_score == 100:
                    break   

            if best_score >= 95:
                matched_uris.append(best_uri)
            else:
                unmatched += 1

        if matched_uris:
            new_playlist_id = target_service.create_playlist(name=playlist_name)
            target_service.add_tracks_to_playlist(
                new_playlist_id,
                matched_uris
            )                    
    
        # Return Summary
        return {
            "status": "completed",
            "total": len(universal_tracks),
            "matched": len(matched_uris),
            "unmatched": unmatched
        }

    except Exception as exc:
        retry_after = getattr(exc, "retry_after", 5)
        raise self.retry(exc=exc, countdown=retry_after)