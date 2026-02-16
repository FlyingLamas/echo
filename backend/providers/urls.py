from django.urls import path
from .views import SpotifyConnectView, SpotifyCallbackView, SpotifyPlaylistsView

urlpatterns = [
    path('spotify/connect/', SpotifyConnectView.as_view(), name='spotify-connect'),
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify-callback'),
    path('spotify/playlists/', SpotifyPlaylistsView.as_view(), name='spotify-playlists'),
]
