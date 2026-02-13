from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import ServiceAccount
from .serializers import ServiceAccountSerializers
from rest_framework.response import Response

class ServiceAccountListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = ServiceAccount.objects.filter(user = request.user)
        serializer = ServiceAccountSerializers
        return Response(serializer.data)
    