"""
LDAP models for RADIUS schema.

This module provides:
- RadiusProfile: User RADIUS profile attributes (auxiliary class)
"""

from typing import List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class RadiusProfile(LDAPModel):
    """User RADIUS profile model.

    Based on freeradius.schema radiusprofile.
    AUXILIARY object class (meant to be added to inetOrgPerson entries).

    MAY attributes from the schema:
    - radiusAuthType, radiusPasswordRetry, radiusServiceType
    - radiusFramedIPAddress, radiusFramedIPNetmask, radiusFramedMTU
    - radiusSessionTimeout, radiusIdleTimeout, radiusSimultaneousUse
    - radiusClass, radiusCallingStationId, radiusFilterId
    - radiusCallbackNumber, radiusCallbackId
    - radiusFramedCompression, radiusFramedProtocol
    - radiusFramedRoute, radiusFramedRouting
    - radiusNASIPAddress
    """

    # Authentication attributes
    radius_auth_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="radiusAuthType",
        help_text="RADIUS authentication type (PAP, CHAP, MSCHAPV2)",
    )
    radius_password_retry = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="radiusPasswordRetry",
        help_text="Maximum number of password retries allowed",
    )
    radius_service_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="radiusServiceType",
        help_text="RADIUS service type (Framed-User, Call-Check, etc.)",
    )

    # Framed network attributes
    radius_framed_ip_address = models.GenericIPAddressField(
        protocol="IPv4",
        blank=True,
        null=True,
        verbose_name="radiusFramedIPAddress",
        help_text="Static IPv4 address to assign",
    )
    radius_framed_ip_netmask = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="radiusFramedIPNetmask",
        help_text="Netmask for framed IP address (e.g., 255.255.255.0)",
    )
    radius_framed_mtu = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=1500,
        verbose_name="radiusFramedMTU",
        help_text="Maximum Transmission Unit size",
    )
    radius_framed_protocol = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="radiusFramedProtocol",
        help_text="Framed protocol (PPP, SLIP)",
    )
    radius_framed_routing = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="radiusFramedRouting",
        help_text="Routing method (none, broadcast, rip)",
    )

    # Session attributes
    radius_session_timeout = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="radiusSessionTimeout",
        help_text="Maximum session duration in seconds",
    )
    radius_idle_timeout = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="radiusIdleTimeout",
        help_text="Idle timeout in seconds before disconnect",
    )
    radius_simultaneous_use = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="radiusSimultaneousUse",
        help_text="Maximum number of simultaneous sessions allowed",
    )

    # Class and filter attributes
    radius_class = models.JSONField(
        blank=True,
        default=list,
        verbose_name="radiusClass",
        help_text="List of RADIUS Class attributes (for VLAN assignment, etc.)",
    )
    radius_calling_station_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="radiusCallingStationId",
        help_text="Calling station identifier (usually MAC address)",
    )
    radius_filter_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="radiusFilterId",
        help_text="Filter ID for applied policies",
    )

    # Callback attributes
    radius_callback_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="radiusCallbackNumber",
        help_text="Phone number to call back",
    )
    radius_callback_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="radiusCallbackId",
        help_text="Callback identifier",
    )

    # Compression and routing
    radius_framed_compression = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="radiusFramedCompression",
        help_text="Compression type (Van Jacobson TCP/IP, VFCOMPRESS)",
    )
    radius_framed_route = models.JSONField(
        blank=True,
        default=list,
        verbose_name="radiusFramedRoute",
        help_text="List of static routes to push",
    )

    # NAS attributes
    radius_nas_ip_address = models.GenericIPAddressField(
        protocol="IPv4",
        blank=True,
        null=True,
        verbose_name="radiusNASIPAddress",
        help_text="IP address of the NAS device",
    )
    radius_nas_identifier = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="radiusNASIdentifier",
        help_text="Identifier for the NAS device",
    )

    ldap_base_dn = ""
    object_classes = ["radiusprofile"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_radius_profiles"
        verbose_name = "RADIUS Profile"
        verbose_name_plural = "RADIUS Profiles"

    def __str__(self) -> str:
        return f"RADIUS Profile for {getattr(self, 'uid', 'unknown')}"

    @property
    def dn(self) -> str:
        """Get the DN (this is auxiliary, so DN comes from parent)."""
        return getattr(self, "_dn", "")

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
