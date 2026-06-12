"""Admin configuration for OpenLDAP CORBA models."""

from django.contrib import admin

from ..models.corba import CorbaContainer, CorbaObject, CorbaObjectReference


@admin.register(CorbaContainer)
class CorbaContainerAdmin(admin.ModelAdmin):
    """Admin for CORBA Container."""
    list_display = ("cn", "description")
    search_fields = ("cn", "description")
    fields = ("cn", "description")


@admin.register(CorbaObject)
class CorbaObjectAdmin(admin.ModelAdmin):
    """Admin for CORBA Object."""
    list_display = ("cn", "corba_repository_id", "description")
    search_fields = ("cn", "corba_repository_id", "description")
    fields = ("cn", "corba_repository_id", "description")


@admin.register(CorbaObjectReference)
class CorbaObjectReferenceAdmin(admin.ModelAdmin):
    """Admin for CORBA Object Reference."""
    list_display = ("cn", "corba_ior", "description")
    search_fields = ("cn", "corba_ior", "description")
    fields = ("cn", "corba_ior", "description")
