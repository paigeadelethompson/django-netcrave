"""Admin for PowerDNS models."""

from django.contrib import admin

from ..models.powerdns import PDNSDomain, PDNSRecord


@admin.register(PDNSDomain)
class PDNSDomainAdmin(admin.ModelAdmin):
    """Admin for DNS zones."""

    list_display = ("dc", "dnsttl", "pdns_domain_type", "soa_serial")
    search_fields = ("dc",)
    list_filter = ("pdns_domain_type",)

    fieldsets = (
        (
            "Zone Information",
            {
                "fields": (
                    "dc",
                    "dnsttl",
                    "dnsclass",
                    "pdns_domain_type",
                )
            },
        ),
        (
            "Master/Slave Configuration",
            {
                "fields": ("master_ips",),
                "classes": ("collapse",),
            },
        ),
        (
            "SOA Record",
            {
                "fields": (
                    ("soa_serial", "soa_refresh"),
                    ("soa_retry", "soa_expiry"),
                    "soa_minimum",
                    ("soa_record",),
                )
            },
        ),
        (
            "NS Records",
            {
                "fields": ("ns_records",),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(PDNSRecord)
class PDNSRecordAdmin(admin.ModelAdmin):
    """Admin for DNS records."""

    list_display = ("dc", "record_type", "value_display", "priority", "active")
    search_fields = ("dc", "value")
    list_filter = ("record_type", "active")
    list_editable = ("active",)
    ordering = ("record_type", "dc")

    fieldsets = (
        (
            "Record Information",
            {
                "fields": (
                    ("dc", "record_type"),
                    "dnsttl",
                )
            },
        ),
        (
            "Value",
            {
                "fields": ("value",),
                "description": "Enter the record value based on type",
            },
        ),
        (
            "Priority/Weight (for MX, SRV)",
            {
                "fields": (("priority", "weight", "port"),),
                "classes": ("collapse",),
            },
        ),
        (
            "DNSSEC Fields",
            {
                "fields": (
                    ("flags", "protocol"),
                    ("algorithm", "public_key"),
                    ("key_tag", "digest_type", "digest"),
                    "signature",
                    "type_covered",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    ("notes",),
                    "active",
                )
            },
        ),
    )

    def value_display(self, obj):
        """Display formatted value."""
        return obj.get_value_display()

    value_display.short_description = "Value"
