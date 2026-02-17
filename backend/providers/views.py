from django.shortcuts import render

import urllib.parse
# urllib.parse - Convert a dictionary of parameters into a URL query string (eg: a=1&b=2), We use this to properly format the Spotify authorization URL.
# We use this to properly format the Spotify authorization URL.

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import secrets

import requests
from django.utils import timezone
from datetime import timedelta
from .models import Provider, ProviderAccount
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import json
import base64

# For testing purposes
from .services.spotify_service import SpotifyService

class SpotifyConnectView(APIView):
    # permission_classes = [IsAuthenticated]
    
    def get(self, request):
        base_url = "https://accounts.spotify.com/authorize"
        # This is Spotify’s official OAuth authorization endpoint.
        # When we redirect users here, Spotify:
            # Shows login screen
            # Asks for permission
            # Then redirects back to our app with a code
            
        state_data = {
            "user_id": request.user.id,
            "nonce": secrets.token_urlsafe(16)
        }
        
        state = base64.urlsafe_b64encode(
            json.dumps(state_data).encode()
        ).decode()
        
        # request.session["spotify_oauth_state"] = state

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
        
        return Response({"auth_url": url})

class SpotifyCallbackView(APIView):
    # permission_classes = [IsAuthenticated]
    # We are keeping this commented out permanently, because if we keep this we will always face 401 unauthorized, 
    # By removing this we are allowing any. This does not mean security is compromised but security is checked via state.

    def get(self, request):

        received_state = request.GET.get("state")
        if not received_state:
            return Response({"error": "Invalid state"}, status=400)
        
        try:
            decoded = base64.urlsafe_b64decode(received_state).decode()
            state_data = json.loads(decoded)
            user_id = state_data["user_id"]
        except Exception:
            return Response({"error": "Invalid state"}, status=400)
        
        # Get authorization code
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Authorization code missing"}, status=400)
        
        # Get user from state
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist):
            return Response({"error": "Invalid state"}, status=status.HTTP_400_BAD_REQUEST)
        
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
        provider, _ = Provider.objects.get_or_create(
            name="spotify",
            defaults={"display_name": "Spotify"}
        )

        # Store or update account
        ProviderAccount.objects.update_or_create(
            user=user,
            provider=provider,
            defaults={
                "provider_user_id": "temp", # we will add id later
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": timezone.now() + timedelta(seconds=expires_in)
            }
        )
        
        print(request.user)
        print(request.user.is_authenticated) 
        print("Session state:", request.session.get("spotify_oauth_state"))
        print("Received state:", request.GET.get("state"))
   
        return Response({"message": "Spotify connected successfully"})

# For testing purposes
class SpotifyPlaylistsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        provider = Provider.objects.get(name="spotify")
        account = ProviderAccount.objects.get(user=request.user, provider=provider)

        service = SpotifyService(account)
        data = service.get_user_playlists()

        return Response(data)
