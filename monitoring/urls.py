from django.contrib import admin
from django.urls import path
from dashboard import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("api/<int:api_id>/", views.api_detail, name="api_detail"),  # ✅ correction
    path("apis/up/", views.api_up_list, name="api_up_list"),
]
