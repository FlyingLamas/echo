from django.shortcuts import render

import urllib.parse
# urllib.parse - Convert a dictionary of parameters into a URL query string (eg: a=1&b=2), We use this to properly format the Spotify authorization URL.
# We use this to properly format the Spotify authorization URL.

from django.conf import settings
from django.http import HttpResponseRedirect
# This is used to redirect the user to another URL. 
# When the user hits this endpoint, we don’t return JSON, we redirect them to Spotify’s login page.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import secrets

import requests
from django.utils import timezone
from datetime import timedelta
from .models import Provider, ProviderAccount
from rest_framework.response import Response

# For testing purposes
from .services.spotify_service import SpotifyService

class SpotifyConnectView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        base_url = "https://accounts.spotify.com/authorize"
        # This is Spotify’s official OAuth authorization endpoint.
        # When we redirect users here, Spotify:
            # Shows login screen
            # Asks for permission
            # Then redirects back to our app with a code
        
        state = secrets.token_urlsafe(32)
        request.session["spotify_oauth_state"] = state

        params = {
            "response_type": "code",
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": "playlist-read-private playlist-modify-public playlist-modify-private",
            "state": state,   
        }

        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        # urllib.parse.urlencode(params) converts the dictionary that is params and converts it into following
        # response_type=code&client_id=abc123&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback%2F&scope=playlist-read-private+playlist-modify-public
        # Here key: value pair become key=value, like "response_type": "code" to response_type=code
        # Pairs are joined with &
        # Special characters are encoded, http://localhost:8000/callback/ becomes http%3A%2F%2Flocalhost%3A8000%2Fcallback%2F
        # Because: :/ spaces etc. are not safe in URLs, Browsers require percent encoding and Spaces become +.
        # The ? separates: main URL  |  query parameters
        # Everything after ? is query string.
        
        return HttpResponseRedirect(url)

class SpotifyCallbackView(APIView):
    permission_classes = []
    # Removed IsAuthenticated, spotify is redirecting the user, and OAuth is proving identity.

    def get(self, request):
        # Validate state (CSRF protection)
        stored_state = request.session.get("spotify_oauth_state")
        received_state = request.GET.get("state")

        if not stored_state or stored_state != received_state:
            return Response({"error": "Invalid state"}, status=400)
        
        # delete state after validation
        request.session.pop("spotify_oauth_state", None)
        
        # Get authorization code
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Authorization code missing"}, status=400)
        
        # Exchange code for tokens
        token_url = "https://accounts.spotify.com/api/token"

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }

        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            return Response({"error": "Failed to get token"}, status=400)
        
        token_data = response.json()

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data["expires_in"]

        # Get provider
        provider = Provider.objects.get(name="spotify")

        # Store or update account
        ProviderAccount.objects.update_or_create(
            user=request.user,
            provider=provider,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": timezone.now() + timedelta(seconds=expires_in)
            }
        )

        return Response({"message": "Spotify connected successfully"})

# For testing purposes
class SpotifyPlaylistsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        provider = Provider.objects.get(name="spotify")
        account = ProviderAccount.objects.get(user=request.user, provider=provider)

        service = SpotifyService(account)
        data = service.get_user_playlists()

        return Response(data)
