from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin  # noqa F401
from django.urls import path

from app.accounts.admin import admin_site
from app.api import api

urlpatterns = [
    path("admin/", admin_site.urls),
    path("api/v1/", api.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
