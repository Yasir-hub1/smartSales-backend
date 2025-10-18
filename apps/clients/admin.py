from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'client_type', 'created_at']
    list_filter = ['client_type', 'created_at']
    search_fields = ['name', 'email']
