"""Admin for OpenDKIM model."""

from django.contrib import admin

from ..models.opendkim import DKIM


@admin.register(DKIM)
class DKIMAdmin(admin.ModelAdmin):
    """Admin for DKIM selector and key entries."""

    list_display = ("cn", "dkim_selector", "dkim_domain", "description")
    search_fields = ("cn", "dkim_selector", "dkim_domain")
    list_filter = ()

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    ("cn",),
                    "dkim_selector",
                )
            },
        ),
        (
            "Domain Info",
            {
                "fields": (
                    ("dkim_identity",),
                    ("dkim_domain",),
                )
            },
        ),
        (
            "Key",
            {
                "fields": (("dkim_key",),),
                "classes": ("collapse",),
            },
        ),
        (
            "Description",
            {
                "fields": (("description",),),
            },
        ),
    )
