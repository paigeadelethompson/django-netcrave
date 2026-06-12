"""Admin for RADIUS profile model."""

from django.contrib import admin

from ..models.radius import RadiusProfile


@admin.register(RadiusProfile)
class RadiusProfileAdmin(admin.ModelAdmin):
    """Admin for RADIUS profiles."""

    list_display = (
        "radius_auth_type",
        "radius_service_type",
        "radius_framed_ip_address",
        "radius_session_timeout",
        "radius_simultaneous_use",
    )
    search_fields = ("uid",)
    list_filter = ("radius_auth_type",)

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    ("radius_auth_type",),
                    ("radius_password_retry",),
                    ("radius_service_type",),
                )
            },
        ),
        (
            "Framed IP",
            {
                "fields": (
                    ("radius_framed_ip_address",),
                    ("radius_framed_ip_netmask",),
                    ("radius_framed_protocol",),
                    ("radius_framed_routing",),
                )
            },
        ),
        (
            "Session Settings",
            {
                "fields": (
                    ("radius_session_timeout",),
                    ("radius_idle_timeout",),
                    ("radius_simultaneous_use",),
                )
            },
        ),
        (
            "MTU & Compression",
            {
                "fields": (
                    ("radius_framed_mtu",),
                    ("radius_framed_compression",),
                )
            },
        ),
        (
            "Class & Filter",
            {
                "fields": (
                    ("radius_class",),
                    ("radius_calling_station_id",),
                    ("radius_filter_id",),
                )
            },
        ),
        (
            "Callback",
            {
                "fields": (
                    ("radius_callback_number",),
                    ("radius_callback_id",),
                )
            },
        ),
        (
            "Routes",
            {
                "fields": (("radius_framed_route",),),
                "classes": ("collapse",),
            },
        ),
    )
