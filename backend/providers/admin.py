from django.contrib import admin

from .models import Provider, ProviderAccount

admin.site.register(Provider)
admin.site.register(ProviderAccount)
