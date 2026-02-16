from django.db import models
from django.conf import settings

# Create your models here.

class ServiceAccount(models.Model):
    PROVIDER_CHOICES = [
        ("spotify", "Spotify"),
        ("youtube", "YouTube Music"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    provider = models.CharField(max_length = 50, choices = PROVIDER_CHOICES)
    
    access_token = models.TextField()
    refresh_token = models.TextField(blank= True, null= True)
    token_expires_at = models.DateTimeField(blank=True, null=True, )
    created_at = models.DateTimeField(auto_now_add=True)

    # understand this concept deeply, why both required below, not understaood right now.    
    class Meta:
        unique_together = ("user", "provider")
