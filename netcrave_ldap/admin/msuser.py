"""Admin for Microsoft user model."""

from django.contrib import admin

from ..models.msuser import MsUser


@admin.register(MsUser)
class MsUserAdmin(admin.ModelAdmin):
    """Admin for Windows users."""

    list_display = (
        "cn",
        "uid",
        "s_am_account_name",
        "mail",
        "account_disabled",
        "password_never_expires",
    )
    search_fields = ("cn", "uid", "s_am_account_name", "mail")
    list_filter = ("account_disabled",)

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    ("cn", "sn"),
                    ("given_name",),
                    ("uid", "mail"),
                )
            },
        ),
        (
            "Windows Account",
            {
                "fields": (
                    ("s_am_account_name",),
                    ("user_principal_name",),
                )
            },
        ),
        (
            "Account Status",
            {
                "fields": (
                    ("account_disabled",),
                    ("password_expired",),
                    ("password_never_expires",),
                    ("dont_require_pre_auth",),
                )
            },
        ),
        (
            "Profile Settings",
            {
                "fields": (
                    ("profile_path", "logon_script"),
                    ("home_directory", "home_drive"),
                )
            },
        ),
        (
            "Directory Services",
            {
                "fields": (
                    ("object_sid",),
                    ("user_account_control",),
                )
            },
        ),
    )
