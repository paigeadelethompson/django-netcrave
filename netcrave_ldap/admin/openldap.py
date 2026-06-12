"""Admin for OpenLDAP models (computer, RADIUS client)."""

from django.contrib import admin

from ..models.openldap import Computer, RadiusClient


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    """Admin for computer entries."""

    list_display = ("cn", "ip_host_number_list", "mac_address", "description")
    search_fields = ("cn", "ip_host_number", "mac_address")
    list_filter = ()

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    ("cn",),
                    "ou",
                )
            },
        ),
        (
            "Network",
            {
                "fields": (
                    ("ip_host_number",),
                    ("mac_address",),
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

    def ip_host_number_list(self, obj):
        """Display IP addresses as comma-separated list."""
        return ", ".join(obj.ip_host_number) if obj.ip_host_number else "-"


@admin.register(RadiusClient)
class RadiusClientAdmin(admin.ModelAdmin):
    """Admin for RADIUS clients."""

    list_display = (
        "cn",
        "radius_client_shortname",
        "radius_client_type",
        "description",
    )
    search_fields = ("cn", "radius_client_secret")
    list_filter = ()

    fieldsets = (
        (
            "Client Information",
            {
                "fields": (
                    ("cn",),
                    "radius_client_shortname",
                )
            },
        ),
        (
            "Secret",
            {
                "fields": (("radius_client_secret",),),
                "classes": ("collapse",),
            },
        ),
        (
            "Type & Server",
            {
                "fields": (
                    ("radius_client_type",),
                    ("radius_client_virtual_server",),
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
