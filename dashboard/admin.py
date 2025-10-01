from django.contrib import admin
from .models import MonitoredAPI

@admin.register(MonitoredAPI)
class MonitoredAPIAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created_at")
