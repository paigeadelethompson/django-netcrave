"""Admin configuration for COSINE schema models (RFC1274)."""

from django.contrib import admin

from ..models.cosine import (
    PilotObject,
    PilotPerson,
    Account,
    Document,
    Room,
    Domain,
    DNSDomain,
    DomainRelatedObject,
    FriendlyCountry,
    SimpleSecurityObject,
    PilotOrganization,
)


@admin.register(PilotObject)
class PilotObjectAdmin(admin.ModelAdmin):
    """Admin for Pilot Object."""
    list_display = ("cn", "info", "description")
    search_fields = ("cn", "info", "description")
    fields = ("cn", "info", "photo", "manager", "unique_identifier", "description")


@admin.register(PilotPerson)
class PilotPersonAdmin(admin.ModelAdmin):
    """Admin for Pilot Person."""
    list_display = ("cn", "userid", "rfc822_mailbox", "description")
    search_fields = ("cn", "userid", "rfc822_mailbox", "description")
    fields = (
        "cn",
        "userid",
        "text_encoded_or_address",
        "rfc822_mailbox",
        "favourite_drink",
        "room_number",
        "user_class",
        "home_telephone_number",
        "home_postal_address",
        "secretary",
        "personal_title",
        "preferred_delivery_method",
        "business_category",
        "janet_mailbox",
        "other_mailbox",
        "mobile_telephone_number",
        "pager_telephone_number",
        "organizational_status",
        "mail_preference_option",
        "personal_signature",
        "description",
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Admin for Account."""
    list_display = ("cn", "description", "host")
    search_fields = ("cn", "description", "host")
    fields = (
        "cn",
        "description",
        "see_also",
        "locality_name",
        "organization_name",
        "organizational_unit_name",
        "host",
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin for Document."""
    list_display = ("document_identifier", "common_name", "document_version")
    search_fields = ("document_identifier", "common_name", "document_title")
    fields = (
        "document_identifier",
        "common_name",
        "description",
        "see_also",
        "locality_name",
        "organization_name",
        "organizational_unit_name",
        "document_title",
        "document_version",
        "document_author",
        "document_location",
        "document_publisher",
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin for Room."""
    list_display = ("cn", "room_number", "telephone_number")
    search_fields = ("cn", "room_number", "description")
    fields = (
        "cn",
        "room_number",
        "description",
        "see_also",
        "telephone_number",
    )


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Admin for Domain."""
    list_display = ("dc", "organization_name", "description")
    search_fields = ("dc", "organization_name", "description")
    fields = (
        "dc",
        "associated_name",
        "organization_name",
        "description",
        "business_category",
        "see_also",
        "search_guide",
        "user_password",
    )


@admin.register(DNSDomain)
class DNSDomainAdmin(admin.ModelAdmin):
    """Admin for DNS Domain."""
    list_display = ("dc", "mx_record", "ns_record")
    search_fields = ("dc", "mx_record", "a_record")
    fields = (
        "dc",
        "a_record",
        "md_record",
        "mx_record",
        "ns_record",
        "soa_record",
        "cname_record",
    )


@admin.register(DomainRelatedObject)
class DomainRelatedObjectAdmin(admin.ModelAdmin):
    """Admin for Domain Related Object."""
    list_display = ("associated_domain", "description")
    search_fields = ("associated_domain", "description")
    fields = ("cn", "associated_domain", "description")


@admin.register(FriendlyCountry)
class FriendlyCountryAdmin(admin.ModelAdmin):
    """Admin for Friendly Country."""
    list_display = ("co", "description")
    search_fields = ("co", "description")
    fields = ("co", "description", "search_guide")


@admin.register(SimpleSecurityObject)
class SimpleSecurityObjectAdmin(admin.ModelAdmin):
    """Admin for Simple Security Object."""
    list_display = ("cn", "description")
    search_fields = ("cn", "description")
    fields = ("cn", "user_password", "description")


@admin.register(PilotOrganization)
class PilotOrganizationAdmin(admin.ModelAdmin):
    """Admin for Pilot Organization."""
    list_display = ("organization_name", "organizational_unit_name", "building_name")
    search_fields = ("organization_name", "organizational_unit_name", "building_name")
    fields = (
        "cn",
        "organization_name",
        "organizational_unit_name",
        "building_name",
        "description",
    )
