"""Admin for ldapns schema models."""

from django.contrib import admin

from ..models.ldapns import AuthorizedServiceObject, HostObject, LoginStatusObject


@admin.register(AuthorizedServiceObject)
class AuthorizedServiceObjectAdmin(admin.ModelAdmin):
    """Admin for GSS-API authorized service objects."""

    list_display = ("cn", "authorized_service_list")
    search_fields = ("cn",)
    list_filter = ()

    fieldsets = (
        (
            "Identity",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Authorized Services",
            {
                "fields": (("authorized_service",),),
            },
        ),
    )

    def authorized_service_list(self, obj):
        """Display authorized services as comma-separated list."""
        return ", ".join(obj.authorized_service) if obj.authorized_service else "-"


@admin.register(HostObject)
class HostObjectAdmin(admin.ModelAdmin):
    """Admin for host attribute objects."""

    list_display = ("cn", "host_list")
    search_fields = ("cn",)
    list_filter = ()

    fieldsets = (
        (
            "Identity",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Hosts",
            {
                "fields": (("host",),),
            },
        ),
    )

    def host_list(self, obj):
        """Display hosts as comma-separated list."""
        return ", ".join(obj.host) if obj.host else "-"


@admin.register(LoginStatusObject)
class LoginStatusObjectAdmin(admin.ModelAdmin):
    """Admin for login status tracking objects."""

    list_display = ("cn", "login_status_list")
    search_fields = ("cn",)
    list_filter = ()

    fieldsets = (
        (
            "Identity",
            {
                "fields": (("cn",),),
            },
        ),
        (
            "Login Status",
            {
                "fields": (("login_status",),),
            },
        ),
    )

    def login_status_list(self, obj):
        """Display login status entries as comma-separated list."""
        return ", ".join(obj.login_status) if obj.login_status else "-"
