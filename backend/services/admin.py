from django.contrib import admin

# Register your models here.

from .models import ServiceAccount

admin.site.register(ServiceAccount)
