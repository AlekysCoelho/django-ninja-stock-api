from django.contrib import admin  # noqa F401
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
