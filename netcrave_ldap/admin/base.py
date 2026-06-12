"""
Base admin classes for LDAP models.
"""

from django.contrib import admin

from ..models.base import LDAPModel


class LDAPAdmin(admin.ModelAdmin):
    """Base admin class with common LDAP functionality."""

    list_per_page = 25
    save_as = True
    save_on_top = True

    def get_search_results(self, request, queryset, search_term):
        """Apply custom search logic."""
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        return queryset, use_distinct


class DNDisplayMixin:
    """Mixin to display DN in admin interface."""

    def get_dn(self, obj):
        """Display the distinguished name."""
        if hasattr(obj, "dn"):
            return obj.dn
        return None

    get_dn.short_description = "Distinguished Name"
    get_dn.admin_order_field = "dn"
