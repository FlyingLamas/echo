from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import TransferJob
from .serializers import TransferJobSerializer
from rest_framework.response import Response

class TransferJobCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        job = TransferJob.objects.create(
            user = request.user,
            source_provider = data["source_provider"],
            destination_provider = data["destination_provider"],
            playlist_name = data["playlist_name"],
        )
