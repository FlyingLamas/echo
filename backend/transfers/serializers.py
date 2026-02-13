from .models import TransferJob
from rest_framework import serializers

class TransferJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferJob
        fields = "__all__"
        read_only_fields = ["status", "transferred_tracks", "failed_tracks"]
