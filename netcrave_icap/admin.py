"""Admin configuration for netcrave_icap."""

from django.contrib import admin

from .models import ICAPUserProfile, ICAPService


@admin.register(ICAPUserProfile)
class ICAPUserProfileAdmin(admin.ModelAdmin):
    """Admin for ICAP user profiles."""

    list_display = ("user_dn", "allow_icap_access", "max_connections")
    list_filter = ("allow_icap_access",)


@admin.register(ICAPService)
class ICAPServiceAdmin(admin.ModelAdmin):
    """Admin for ICAP service configurations."""

    list_display = (
        "cn",
        "icap_service_host",
        "icap_service_port",
        "icap_authentication_type",
        "icap_allow_anonymous",
    )
    search_fields = ("cn", "icap_service_host", "icap_kerberos_service_principal")
    list_filter = ("icap_authentication_type", "icap_allow_anonymous")
