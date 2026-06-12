"""Admin for Asterisk models."""

from django.contrib import admin

from ..models.asterisk import (
    AsteriskConfig,
    AsteriskExtension,
    AsteriskIAXUser,
    AsteriskSIPUser,
    AsteriskVoiceMail,
)


@admin.register(AsteriskExtension)
class AsteriskExtensionAdmin(admin.ModelAdmin):
    """Admin for Asterisk extensions."""

    list_display = ("cn", "ast_context", "ast_extension", "ast_priority")
    search_fields = ("cn", "ast_context", "ast_extension")
    list_filter = ("ast_context",)

    fieldsets = (
        (
            "Extension",
            {
                "fields": (
                    ("cn", "ast_context"),
                    ("ast_extension", "ast_priority"),
                )
            },
        ),
        (
            "Dialplan",
            {
                "fields": (
                    ("ast_application",),
                    "ast_application_data",
                )
            },
        ),
    )


@admin.register(AsteriskIAXUser)
class AsteriskIAXUserAdmin(admin.ModelAdmin):
    """Admin for IAX users."""

    list_display = (
        "cn",
        "ast_account_name",
        "ast_context",
        "ast_extension",
        "ast_auth_type",
    )
    search_fields = ("cn", "ast_account_name")
    list_filter = ("ast_auth_type",)

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    ("cn",),
                    "ast_account_name",
                )
            },
        ),
        (
            "Extension",
            {
                "fields": (
                    ("ast_context", "ast_extension"),
                    ("ast_priority",),
                )
            },
        ),
        (
            "Authentication",
            {
                "fields": (
                    ("ast_md5_secret",),
                    ("ast_username", "ast_auth_type"),
                    ("ast_account_host", "ast_port"),
                )
            },
        ),
        (
            "Network",
            {
                "fields": (
                    ("ast_account_transport",),
                    ("ast_account_nat",),
                )
            },
        ),
        (
            "Codec Settings",
            {
                "fields": (
                    ("ast_account_disallowed_codec",),
                    ("ast_account_allowed_codec",),
                )
            },
        ),
    )


@admin.register(AsteriskSIPUser)
class AsteriskSIPUserAdmin(admin.ModelAdmin):
    """Admin for SIP users."""

    list_display = (
        "cn",
        "ast_account_name",
        "ast_context",
        "ast_extension",
        "ast_transport",
    )
    search_fields = ("cn", "ast_account_name")
    list_filter = ("ast_transport",)

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    ("cn",),
                    "ast_account_name",
                )
            },
        ),
        (
            "Extension",
            {
                "fields": (
                    ("ast_context", "ast_extension"),
                    ("ast_priority",),
                )
            },
        ),
        (
            "Credentials",
            {
                "fields": (
                    ("ast_account_secret",),
                    ("ast_account_transport",),
                )
            },
        ),
        (
            "NAT Settings",
            {
                "fields": (("ast_account_nat",),),
            },
        ),
        (
            "Codec Settings",
            {
                "fields": (
                    ("ast_codecs",),
                    ("ast_allow",),
                    ("ast_direct_media", "ast_account_video_support"),
                )
            },
        ),
        (
            "Call Limits",
            {
                "fields": (
                    ("ast_account_call_limit",),
                    ("ast_account_call_group", "ast_account_pickup_group"),
                )
            },
        ),
    )


@admin.register(AsteriskVoiceMail)
class AsteriskVoiceMailAdmin(admin.ModelAdmin):
    """Admin for Asterisk voicemail."""

    list_display = ("cn", "ast_voicemail_mailbox", "ast_context")
    search_fields = ("cn", "ast_voicemail_mailbox")
    list_filter = ("ast_context",)

    fieldsets = (
        (
            "Voicemail",
            {
                "fields": (
                    ("cn",),
                    "ast_voicemail_mailbox",
                )
            },
        ),
        (
            "Password & Access",
            {
                "fields": ("ast_voicemail_password",),
            },
        ),
        (
            "Notifications",
            {
                "fields": (
                    ("ast_voicemail_fullname",),
                    ("ast_voicemail_email", "ast_voicemail_pager"),
                )
            },
        ),
        (
            "Options",
            {
                "fields": (
                    ("ast_context", "ast_voicemail_options"),
                    "ast_voicemail_context",
                )
            },
        ),
    )


@admin.register(AsteriskConfig)
class AsteriskConfigAdmin(admin.ModelAdmin):
    """Admin for Asterisk configuration."""

    list_display = (
        "cn",
        "ast_config_filename",
        "ast_config_category",
        "ast_config_variable_name",
    )
    search_fields = ("cn", "ast_config_category")
    list_filter = ("ast_config_filename",)

    fieldsets = (
        (
            "Configuration Entry",
            {
                "fields": (
                    ("cn",),
                    "ast_config_filename",
                )
            },
        ),
        (
            "Category & Variable",
            {
                "fields": (
                    ("ast_config_category",),
                    ("ast_config_variable_name",),
                    ("ast_config_variable_value",),
                )
            },
        ),
        (
            "Options",
            {
                "fields": (("ast_config_commented",),),
                "classes": ("collapse",),
            },
        ),
    )
