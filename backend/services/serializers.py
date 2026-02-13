# The Reason we are adding this file depends on asking the following questions, 
    # 1. Is the frontend sending data to the backend app - If yes, create it
    # 2. Is the frontend requesting a list of data - If yes, create it
    # 3. Is the logic simple or complex - Simple can be handled in views as well.
# Also we dont want to expose our access and refresh tokens, as we need controlled api output

from rest_framework import serializers
from .models import ServiceAccount

class ServiceAccountSerializers(serializers.ModelSerializer):
    model = ServiceAccount
    fields = ["id", "provider", "created_at"]
