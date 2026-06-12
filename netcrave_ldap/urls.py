"""
URL configuration for ldap_management project.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("", admin.site.urls),
]
