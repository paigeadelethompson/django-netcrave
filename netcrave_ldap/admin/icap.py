"""Admin for Netcrave ICAP models."""

from django.contrib import admin

from ..models.icap import IcapService, IcapUser


@admin.register(IcapService)
class IcapServiceAdmin(admin.ModelAdmin):
    """Admin for ICAP service configuration."""

    list_display = (
        "cn",
        "icap_service_host",
        "icap_service_port",
        "icap_max_body_size",
        "description",
    )
    search_fields = ("cn", "icap_service_host")
    list_filter = ("icap_authentication_type",)

    fieldsets = (
        (
            "Service Identity",
            {
                "fields": (
                    ("cn",),
                    "icap_service_name",
                )
            },
        ),
        (
            "Network",
            {
                "fields": (
                    ("icap_service_host",),
                    ("icap_service_port",),
                )
            },
        ),
        (
            "Limits",
            {
                "fields": (
                    ("icap_max_body_size",),
                    ("iap_preview_size",),
                    ("iap_max_connections",),
                )
            },
        ),
        (
            "Request/Response Headers",
            {
                "fields": (
                    ("iap_methods_supported",),
                    ("iap_request_headers",),
                    ("iap_response_headers",),
                    ("iap_allow_headers",),
                )
            },
        ),
        (
            "Authentication",
            {
                "fields": (
                    ("iap_authentication_type",),
                    ("iap_kerberos_service_principal",),
                    ("iap_kerberos_keytab",),
                    ("iap_allow_anonymous",),
                )
            },
        ),
        (
            "Transfer Settings",
            {
                "fields": (
                    ("iap_transfer_complete",),
                )
            },
        ),
        (
            "Description",
            {
                "fields": (("description",),),
            },
        ),
    )


@admin.register(IcapUser)
class IcapUserAdmin(admin.ModelAdmin):
    """Admin for ICAP user access control."""

    list_display = (
        "cn",
        "iap_allow_icap_access",
        "iap_max_connections_per_user",
    )
    search_fields = ("cn",)
    list_filter = ("iap_allow_icap_access",)

    fieldsets = (
        (
            "User Identity",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Access Control",
            {
                "fields": (
                    ("iap_allow_icap_access",),
                    ("iap_max_connections_per_user",),
                )
            },
        ),
    )
