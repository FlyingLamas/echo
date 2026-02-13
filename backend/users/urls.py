from django.urls import path
from .views import test_protected, LogoutView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    path("test/", test_protected, name = "test-protected"),
    
    path("login/", TokenObtainPairView.as_view(), name = "token-obtain-pair"),
    path("refresh/", TokenRefreshView.as_view(), name = "token-refresh"),
    path("logout/", LogoutView.as_view(), name = "logout")
]
