import requests
from django.utils import timezone
from ..models import ProviderAccount

class SpotifyService:
    base_url = "https://api.spotify.com/v1"
    # All spotify endpoints start with above url, so instead of repeating it we declare it beforehand.
    
    def __init__(self, provider_account):
        self.account = provider_account
    
    def _get_headers(self):
        """ 
        This builds, HTTP headers, spotify requires Authorization: Bearer ACCESS_TOKEN
        Without this header spotify will return 401 Unauthorized 
        Also underscore methods are used for internal purposes only, so you dont call from outside
        """
        return {
            "Authorization": f"Bearer {self.account.access_token}"
        }
    
    def get_user_playlists(self):
        """
        The endpoint becomes GET https://api.spotify.com/v1/me/playlists
        This returns users playlists, paginated result, default of 20 per page
        """
        url = f"{self.base_url}/me/playlists"
        response = requests.get(url, headers= self._get_headers(), timeout=10)
        # This response makes actual HTTP request to spotify,
        # Here url is the endpoint, headers contain access token, spotify then validates token and returns a json response.
        # me refers to current authenticated user
        
        # If token expires
        if response.status_code == 401:
            self.refresh_access_token()
            response = requests.get(url, headers= self._get_headers, timeout=10)
            
        return response.json()
        # We convert response into python dictionary and return it