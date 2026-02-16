from .models import TransferJob
from rest_framework import serializers

class TransferJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferJob
        fields = "__all__"
        read_only_fields = ["status", "transferred_tracks", "failed_tracks", "total_tracks", "user",]

    # def validate(self, data):
    # if data["source_provider"] == data["destination_provider"]:
    #     raise serializers.ValidationError("Source and destination cannot be same")
    # return data
