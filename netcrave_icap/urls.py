"""URL configuration for netcrave_icap app."""

from django.urls import path

from .views import icap_status_view, icap_responder_view

app_name = "netcrave_icap"

urlpatterns = [
    # ICAP status endpoint
    path("status/", icap_status_view, name="icap-status"),
    # Main ICAP responder endpoint
    path("", icap_responder_view, name="icap-responder"),
]
