from django.db import models
from django.conf import settings

class Provider(models.Model):
    name = models.CharField(max_length=50, unique=True)  # spotify
    display_name = models.CharField(max_length=100)      # Spotify

    def __str__(self):
        return self.display_name

class ProviderAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_accounts"
    )
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE,
        related_name="accounts")

    provider_user_id = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "provider")

    def __str__(self):
        return f"{self.user.email} - {self.provider.name}"
