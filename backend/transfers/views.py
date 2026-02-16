from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import TransferJob
from .serializers import TransferJobSerializer
from rest_framework.response import Response
from .services import TransferService

class TransferJobView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        jobs = TransferJob.objects.filter(user=request.user).order_by("-created_at")
        serializer = TransferJobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TransferJobSerializer(data = request.data)
        if serializer.is_valid():
            job = serializer.save(user=request.user)
            updated_job = TransferService.start_transfer(job)
            serializer = TransferJobSerializer(updated_job)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TransferJobDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        try:
            job = TransferJob.objects.get(id=job_id, user=request.user)
            serializer = TransferJobSerializer(job)
            return Response(serializer.data)
        except TransferJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)
        
            