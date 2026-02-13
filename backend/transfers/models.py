from django.db import models
from ..backend import settings

class TransferJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    
    source_provider = models.CharField(max_length = 50)    
    destination_provider = models.CharField(max_length= 50)
    playlist_name = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    total_tracks = models.CharField(default=0)
    transferred_tracks = models.IntegerField(default = 0)    
    failed_tracks = models.IntegerField(default = 0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    