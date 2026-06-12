"""Admin for Postfix models."""

from django.contrib import admin

from ..models.postfix import PostfixAlias, PostfixTransport


@admin.register(PostfixAlias)
class PostfixAliasAdmin(admin.ModelAdmin):
    """Admin for Postfix mail aliases."""

    list_display = ("destination_preview", "mail")
    search_fields = ("mail", "destination")
    list_filter = ()

    fieldsets = (
        (
            "Destination",
            {
                "fields": (("mail",),),
            },
        ),
        (
            "Source Addresses",
            {
                "fields": (
                    ("destination",),
                    "description",
                )
            },
        ),
    )

    def destination_preview(self, obj):
        """Short preview of destinations."""
        return ", ".join(obj.destination[:5]) if len(obj.destination) > 5 else ", ".join(obj.destination)

    destination_preview.short_description = "Sources"


@admin.register(PostfixTransport)
class PostfixTransportAdmin(admin.ModelAdmin):
    """Admin for Postfix transport maps."""

    list_display = ("mail_routing_domain", "transport_type", "transport_next_hop")
    search_fields = ("mail_routing_domain",)
    list_filter = ("transport_type",)

    fieldsets = (
        (
            "Domain Pattern",
            {
                "fields": (("mail_routing_domain",),),
            },
        ),
        (
            "Transport Configuration",
            {
                "fields": (
                    ("transport_type",),
                    ("transport_next_hop",),
                    "description",
                )
            },
        ),
    )
