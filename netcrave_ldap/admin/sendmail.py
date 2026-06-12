"""Admin for Sendmail models."""

from django.contrib import admin

from ..models.sendmail import SendmailMapEntry, SendmailMTA


@admin.register(SendmailMTA)
class SendmailMTAAdmin(admin.ModelAdmin):
    """Admin for Sendmail MTA servers."""

    list_display = ("cn", "sendmail_mta_cluster", "sendmail_mta_host")
    search_fields = ("cn",)

    fieldsets = (
        (
            "MTA Server",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Cluster Configuration",
            {
                "fields": (("sendmail_mta_cluster",),),
            },
        ),
        (
            "Host Information",
            {
                "fields": (("sendmail_mta_host",),),
            },
        ),
        (
            "Description",
            {
                "fields": (("description",),),
            },
        ),
    )


@admin.register(SendmailMapEntry)
class SendmailMapEntryAdmin(admin.ModelAdmin):
    """Admin for Sendmail map entries."""

    list_display = ("sendmail_mta_key", "sendmail_mta_map_name", "value_preview")
    search_fields = ("sendmail_mta_key", "sendmail_mta_value")
    list_filter = ("sendmail_mta_map_name",)

    fieldsets = (
        (
            "Map Entry",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Map Configuration",
            {
                "fields": (
                    ("sendmail_mta_map_name",),
                    ("sendmail_mta_key",),
                    ("sendmail_mta_value",),
                )
            },
        ),
        (
            "Search Options",
            {
                "fields": (("sendmail_mta_map_search",),),
            },
        ),
    )

    def value_preview(self, obj):
        """Short preview of the map value."""
        value = obj.sendmail_mta_value or ""
        if len(value) > 50:
            return value[:47] + "..."
        return value

    value_preview.short_description = "Value"
