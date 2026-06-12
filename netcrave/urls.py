"""
URL configuration for netcrave project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ca/", include("netcrave_ca.urls")),
    path("icap/", include("netcrave_icap.urls")),
]
