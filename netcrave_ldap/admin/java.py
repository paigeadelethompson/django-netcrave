"""Admin configuration for OpenLDAP Java models."""

from django.contrib import admin

from ..models.java import (
    JavaContainer,
    JavaObject,
    JavaSerializedObject,
    JavaMarshalledObject,
    JavaNamingReference,
)


@admin.register(JavaContainer)
class JavaContainerAdmin(admin.ModelAdmin):
    """Admin for Java Container."""
    list_display = ("cn", "description")
    search_fields = ("cn", "description")
    fields = ("cn", "description")


@admin.register(JavaObject)
class JavaObjectAdmin(admin.ModelAdmin):
    """Admin for Java Object."""
    list_display = ("cn", "java_class_name", "description")
    search_fields = ("cn", "java_class_name", "description")
    fields = ("cn", "java_class_name", "java_class_names", "java_codebase",
              "java_doc", "description")


@admin.register(JavaSerializedObject)
class JavaSerializedObjectAdmin(admin.ModelAdmin):
    """Admin for Java Serialized Object."""
    list_display = ("cn", "description")
    search_fields = ("cn", "description")
    fields = ("cn", "java_serialized_data", "description")


@admin.register(JavaMarshalledObject)
class JavaMarshalledObjectAdmin(admin.ModelAdmin):
    """Admin for Java Marshalled Object."""
    list_display = ("cn", "description")
    search_fields = ("cn", "description")
    fields = ("cn", "java_serialized_data", "description")


@admin.register(JavaNamingReference)
class JavaNamingReferenceAdmin(admin.ModelAdmin):
    """Admin for Java Naming Reference."""
    list_display = ("cn", "java_factory", "description")
    search_fields = ("cn", "java_reference_address", "java_factory", "description")
    fields = ("cn", "java_reference_address", "java_factory", "description")
