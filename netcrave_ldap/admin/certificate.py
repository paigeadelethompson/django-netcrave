"""Admin for Netcrave Certificate models."""

from django.contrib import admin

from ..models.certificate import (
    CertificateTemplate,
    CertificateProfile,
    CertificateRecord,
    CertificateAuthority,
)


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    """Admin for certificate template configuration."""

    list_display = ("cn", "certificate_validity_days", "certificate_key_size")
    search_fields = ("cn",)
    list_filter = ()

    fieldsets = (
        (
            "Template Identity",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Validity",
            {
                "fields": (
                    ("certificate_validity_days",),
                    ("certificate_key_size",),
                )
            },
        ),
        (
            "Subject Alternative Names",
            {
                "fields": (("certificate_san_pattern",),),
            },
        ),
        (
            "Key Usage",
            {
                "fields": (
                    ("certificate_usage_server_auth",),
                    ("certificate_usage_client_auth",),
                    ("certificate_usage_email_protection",),
                    ("certificate_usage_code_signing",),
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


@admin.register(CertificateProfile)
class CertificateProfileAdmin(admin.ModelAdmin):
    """Admin for certificate profile configuration."""

    list_display = ("cn", "certificate_template", "certificate_require_kerberos")
    search_fields = ("cn", "certificate_hostnames")
    list_filter = ("certificate_require_kerberos",)

    fieldsets = (
        (
            "Profile Identity",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Template Mapping",
            {
                "fields": (
                    ("certificate_template",),
                    ("certificate_hostnames",),
                )
            },
        ),
        (
            "Access Control",
            {
                "fields": (
                    ("certificate_require_kerberos",),
                    ("certificate_allowed_principals",),
                )
            },
        ),
        (
            "Auto-Renewal",
            {
                "fields": (("certificate_auto_renewal_days",),),
            },
        ),
        (
            "Description",
            {
                "fields": (("description",),),
            },
        ),
    )


@admin.register(CertificateRecord)
class CertificateRecordAdmin(admin.ModelAdmin):
    """Admin for certificate record storage."""

    list_display = ("cn", "certificate_serial_number", "certificate_status")
    search_fields = ("cn", "certificate_serial_number")
    list_filter = ("certificate_status",)

    fieldsets = (
        (
            "Certificate Identity",
            {
                "fields": (
                    ("cn",),
                    ("certificate_serial_number",),
                )
            },
        ),
        (
            "Subject & Issuer",
            {
                "fields": (
                    ("certificate_subject_cn",),
                    ("certificate_issuer_cn",),
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    ("certificate_status",),
                    ("certificate_revoked_at",),
                    ("certificate_revocation_reason",),
                )
            },
        ),
        (
            "Validity Period",
            {
                "fields": (
                    ("certificate_not_before",),
                    ("certificate_not_after",),
                )
            },
        ),
        (
            "Template & Profile",
            {
                "fields": (
                    ("certificate_template",),
                    ("certificate_profile",),
                )
            },
        ),
        (
            "Authorization",
            {
                "fields": (("certificate_auth_principal",),),
            },
        ),
        (
            "Storage Paths",
            {
                "fields": (
                    ("certificate_storage_path",),
                    ("certificate_private_key_path",),
                )
            },
        ),
        (
            "ACME",
            {
                "fields": (("acme_order_id",),),
            },
        ),
    )


@admin.register(CertificateAuthority)
class CertificateAuthorityAdmin(admin.ModelAdmin):
    """Admin for Certificate Authority configuration."""

    list_display = ("cn", "certificate_not_after", "description")
    search_fields = ("cn",)

    fieldsets = (
        (
            "CA Identity",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Expiration",
            {
                "fields": (("certificate_not_after",),),
            },
        ),
        (
            "Description",
            {
                "fields": (("description",),),
            },
        ),
    )
