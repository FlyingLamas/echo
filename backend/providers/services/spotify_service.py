import requests
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from ..models import ProviderAccount

class SpotifyService:
    # All spotify endpoints start with below url, so instead of repeating it we declare it beforehand.
    base_url = "https://api.spotify.com/v1"
        
    def __init__(self, provider_account):
        self.account = provider_account
        
    def _is_token_expired(self):
        """ We always check whether the token have expired or not, in the beginning """
        return timezone.now() >= self.account.expires_at
    
    def _refresh_access_token(self):
        token_url = "https://accounts.spotify.com/api/token"
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.account.refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            raise Exception("Failed to refresh Spotify token")
        
        token_data = response.json()
        
        self.account.access_token = token_data["access_token"]
        expires_in = token_data["expires_in"]
        
        self.account.expires_at = timezone.now() + timedelta(seconds=expires_in)
        self.account.save()
        
    def _ensure_token_valid(self):
        if self._is_token_expired():
            self._refresh_access_token()
            
    def _make_request(self, method, endpoint, params=None, data=None):
        self._ensure_token_valid()
        
        headers = {
            "Authorization": f"Bearer {self.account.access_token}"
        }
        url = f"{self.base_url}{endpoint}"
        
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            json=data
        )
        
        if response.status_code >= 400:
            raise Exception(f"Spotify API error: {response.text}")

        return response.json()

    def get_user_profile(self):
        return self._make_request("GET", "/me")
    
    def get_user_playlists(self):
        self._ensure_token_valid()

        headers = {
            "Authorization": f"Bearer {self.account.access_token}"
        }

        url = "https://api.spotify.com/v1/me/playlists?limit=50"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return {"error": "Failed to fetch playlists"}

        data = response.json()

        playlists = []

        for playlist in data["items"]:
            playlists.append({
                "id": playlist["id"],
                "name": playlist["name"],
                "tracks_total": playlist.get("tracks", {}).get("total", 0),
                "type": "playlist"
            })

        playlists.insert(0, {
            "id": "liked_songs",
            "name": "Liked Songs",
            "tracks_total": None,
            "type": "special"
        })

        return playlists
    
    def get_playlist_tracks(self, playlist_id):
        self._ensure_token_valid()

        headers = {
            "Authorization": f"Bearer {self.account.access_token}"
        }
        
        limit = 100
        offset = 0
        tracks = []
        
        while True:
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items?limit={limit}&offset={offset}"

            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return {"error": "Failed to fetch tracks"}
            
            data = response.json()
            
            for entry in data["items"]:
                track = entry.get("item")
                
                if track and track["type"] == "track":
                    tracks.append({
                        "id": track.get("id"),
                        "name": track["name"],
                        "artists": ", ".join(artist["name"] for artist in track["artists"]),
                        "album": track["album"]["name"],
                        "duration_ms": track["duration_ms"],
                    })
            
            if not data.get("next"):
                break
            
            offset += limit

        return tracks
    
    def get_liked_songs(self):
        self._ensure_token_valid()

        headers = {
            "Authorization": f"Bearer {self.account.access_token}"
        }

        limit = 50
        offset = 0
        liked_tracks = []

        while True:
            url = (
                f"https://api.spotify.com/v1/me/tracks"
                f"?limit={limit}&offset={offset}"
            )

            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return {"error": "Failed to fetch liked songs"}

            data = response.json()

            for entry in data["items"]:
                track = entry["track"]

                liked_tracks.append({
                    "name": track["name"],
                    "artists": ", ".join(
                        artist["name"] for artist in track["artists"]
                    ),
                    "album": track["album"]["name"],
                    "duration_ms": track["duration_ms"]
                })

            if not data.get("next"):
                break

            offset += limit

        return liked_tracks

