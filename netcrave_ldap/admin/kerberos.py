"""Admin for Kerberos models."""

from django.contrib import admin

from ..models.kerberos import KrbPrincipal, KrbPwdPolicy, KrbRealmContainer, KrbTicketPolicy


@admin.register(KrbRealmContainer)
class KrbRealmContainerAdmin(admin.ModelAdmin):
    """Admin for Kerberos realm containers."""

    list_display = ("cn", "krb_up_enabled")
    search_fields = ("cn",)

    fieldsets = (
        (
            "Realm Configuration",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Password Settings",
            {
                "fields": ("krb_up_enabled",),
            },
        ),
        (
            "LDAP Servers",
            {
                "fields": (("krb_ldap_servers",),),
                "classes": ("collapse",),
            },
        ),
        (
            "Encryption Types",
            {
                "fields": (
                    ("krb_supported_enc_salt_types",),
                    ("krb_default_enc_salt_types",),
                )
            },
        ),
        (
            "Policy References",
            {
                "fields": (
                    ("krb_ticket_policy_reference",),
                    ("krb_pwd_policy_reference",),
                )
            },
        ),
        (
            "Kerberos Services",
            {
                "fields": (
                    ("krb_kdc_servers", "krb_pwd_servers"),
                    ("krb_adm_servers",),
                )
            },
        ),
    )


@admin.register(KrbPrincipal)
class KrbPrincipalAdmin(admin.ModelAdmin):
    """Admin for Kerberos principals."""

    list_display = (
        "krb_principal_name",
        "realm",
        "krb_up_enabled",
        "krb_login_failed_count",
    )
    search_fields = ("krb_principal_name",)
    list_filter = ("realm",)

    fieldsets = (
        (
            "Principal Information",
            {
                "fields": (
                    ("krb_principal_name",),
                    "realm",
                )
            },
        ),
        (
            "Canonical Name",
            {
                "fields": (("krb_canonical_name",),),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    ("krb_up_enabled",),
                    ("krb_principal_type",),
                )
            },
        ),
        (
            "Expiration Dates",
            {
                "fields": (
                    ("krb_password_expiration",),
                    ("krb_principal_expiration",),
                )
            },
        ),
        (
            "Authentication Failures",
            {
                "fields": (
                    ("krb_login_failed_count",),
                    ("krb_last_successful_auth",),
                    ("krb_last_failed_auth",),
                )
            },
        ),
        (
            "Policy References",
            {
                "fields": (
                    ("krb_ticket_policy_reference",),
                    ("krb_pwd_policy_reference",),
                )
            },
        ),
        (
            "Ticket Flags",
            {
                "fields": (
                    ("krb_ticket_flags",),
                    ("krb_max_ticket_life",),
                    ("krb_max_renewable_age",),
                )
            },
        ),
        (
            "Delegation & Auth",
            {
                "fields": (
                    ("krb_allowed_to_delegate_to",),
                    ("krb_principal_auth_ind",),
                )
            },
        ),
    )


@admin.register(KrbPwdPolicy)
class KrbPwdPolicyAdmin(admin.ModelAdmin):
    """Admin for Kerberos password policies."""

    list_display = ("cn", "krb_max_pwd_life", "krb_min_pwd_life", "krb_pwd_min_length")
    search_fields = ("cn",)

    fieldsets = (
        (
            "Password Policy",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Lifetime Settings",
            {
                "fields": (
                    ("krb_max_pwd_life",),
                    ("krb_min_pwd_life",),
                )
            },
        ),
        (
            "Complexity Requirements",
            {
                "fields": (
                    ("krb_pwd_min_length",),
                    ("krb_pwd_min_diff_chars",),
                )
            },
        ),
        (
            "Lockout Settings",
            {
                "fields": (
                    ("krb_pwd_max_failure",),
                    ("krb_pwd_lockout_duration",),
                )
            },
        ),
        (
            "History",
            {
                "fields": (("krb_pwd_history_length",),),
            },
        ),
    )


@admin.register(KrbTicketPolicy)
class KrbTicketPolicyAdmin(admin.ModelAdmin):
    """Admin for Kerberos ticket policies."""

    list_display = ("cn", "krb_max_ticket_life", "krb_max_renewable_age")
    search_fields = ("cn",)

    fieldsets = (
        (
            "Ticket Policy",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Lifetime Settings",
            {
                "fields": (
                    ("krb_max_ticket_life",),
                    ("krb_max_renewable_age",),
                )
            },
        ),
        (
            "Ticket Flags",
            {
                "fields": (("krb_ticket_flags",),),
            },
        ),
    )
