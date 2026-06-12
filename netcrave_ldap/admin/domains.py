"""Admin for domain models (users, groups)."""

from django.contrib import admin

from ..models.domains import GroupOfNames, InetOrgPerson, PosixGroup


@admin.register(InetOrgPerson)
class InetOrgPersonAdmin(admin.ModelAdmin):
    """Admin for inetOrgPerson users."""

    list_display = (
        "cn",
        "uid",
        "mail",
        "display_name",
        "uid_number",
        "gid_number",
        "login_shell",
    )
    search_fields = ("cn", "sn", "uid", "mail")
    list_filter = ("login_shell", "ou", "employee_type")
    ordering = ("uid",)

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    ("cn", "sn"),
                    ("uid", "given_name"),
                    "display_name",
                    "mail",
                )
            },
        ),
        (
            "Organization",
            {
                "fields": (
                    ("title", "ou"),
                    ("department_number", "employee_number", "employee_type"),
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    ("telephone_number", "mobile"),
                    ("home_phone", "pager", "facsimile_telephone_number"),
                )
            },
        ),
        (
            "POSIX Account",
            {
                "fields": (
                    ("uid_number", "gid_number"),
                    ("home_directory", "login_shell"),
                    "gecos",
                )
            },
        ),
        (
            "Shadow Password",
            {
                "fields": (
                    ("shadow_last_change", "shadow_min"),
                    ("shadow_max", "shadow_warning"),
                    ("shadow_inactive", "shadow_expire", "shadow_flag"),
                )
            },
        ),
        (
            "Kerberos",
            {
                "fields": (
                    ("krb_principal_name", "krb_canonical_name"),
                    ("krb_up_enabled", "krb_ticket_policy_reference"),
                    ("krb_password_expiration", "krb_principal_expiration"),
                    ("krb_last_successful_auth", "krb_last_failed_auth"),
                    "krb_login_failed_count",
                )
            },
        ),
        (
            "RADIUS",
            {
                "fields": (
                    ("radius_auth_type", "radius_service_type"),
                    ("radius_framed_ip_address", "radius_simultaneous_use"),
                    ("radius_session_timeout", "radius_idle_timeout"),
                )
            },
        ),
    )

    autocomplete_fields = ()

    def get_form(self, request, obj=None, **kwargs):
        """Add help text to fields."""
        form = super().get_form(request, obj, **kwargs)
        return form


@admin.register(PosixGroup)
class PosixGroupAdmin(admin.ModelAdmin):
    """Admin for POSIX groups."""

    list_display = ("cn", "gid_number", "description", "member_count")
    search_fields = ("cn", "description")
    list_filter = ()
    ordering = ("cn",)

    fieldsets = (
        (
            "Group Information",
            {
                "fields": (
                    ("cn", "gid_number"),
                    "description",
                )
            },
        ),
        (
            "Members",
            {
                "fields": (
                    "member_uid",
                    "members_display",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("members_display",)

    def member_count(self, obj):
        return len(obj.member_uid or [])

    def members_display(self, obj):
        if not obj.member_uid:
            return "No members"
        return ", ".join(obj.member_uid)


@admin.register(GroupOfNames)
class GroupOfNamesAdmin(admin.ModelAdmin):
    """Admin for groupOfNames."""

    list_display = ("cn", "member_count", "description")
    search_fields = ("cn", "description")
    list_filter = ()
    ordering = ("cn",)

    fieldsets = (
        (
            "Group Information",
            {
                "fields": (
                    ("cn",),
                    "description",
                    ("ou", "o"),
                )
            },
        ),
        (
            "Members (DNs)",
            {
                "fields": ("members",),
                "classes": ("collapse",),
            },
        ),
    )

    def member_count(self, obj):
        return len(obj.members or [])
