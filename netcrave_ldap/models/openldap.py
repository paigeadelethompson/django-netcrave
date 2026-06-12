"""
LDAP models for OpenLDAP schemas.

This module provides:
- Computer: device + ipHost model for network devices
- RadiusClient: RADIUS client (NAS/AP) registration
"""

from typing import List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class Computer(LDAPModel):
    mac_address='macAddress',
    description='description',
    ou='ou',
)
class Computer(LDAPModel):
    """Computer/device model combining device and ipHost.

    Object Classes:
    - device (structural): Basic device information
    - ipHost (auxiliary): IP address attributes
    - ieee802Device (auxiliary): MAC address support

    MUST (device):
        cn

    MAY (ipHost):
        ipHostNumber, description, manager

    MAY (ieee802Device):
        macAddress
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="hostname",
        help_text="Computer hostname (cn)",
    )
    ip_host_number = models.JSONField(
        blank=True,
        default=list,
        verbose_name="ipHostNumber",
        help_text="List of IP addresses associated with this host",
    )
    mac_address = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name="macAddress",
        help_text="MAC address (format: AA:BB:CC:DD:EE:FF)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Computer description",
    )
    ou = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalUnit",
        help_text="Organizational unit containing this computer",
    )

    ldap_base_dn = settings.LDAP_OU_COMPUTERS + "," + settings.LDAP_BASE_DN
    object_classes = ["device", "ipHost", "ieee802Device"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'ip_host_number': 'ipHostNumber',
        'mac_address': 'macAddress',
        'description': 'description',
        'ou': 'ou',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_computers"
        verbose_name = "Computer"
        verbose_name_plural = "Computers"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this computer."""
        from ..utils.dn import build_computer_dn

        return build_computer_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class RadiusClient(LDAPModel):
    """RADIUS client (NAS/AP) registration.

    Based on freeradius.schema radiusObjectProfile.
    STRUCTURAL object class.

    MUST: cn
    MAY: uid, userPassword, description

    Additional attributes from freeradius schema:
    - radiusClientIdentifier (IP or hostname)
    - radiusClientSecret
    - radiusClientShortname
    - radiusClientType
    - radiusClientComment
    - radiusClientVirtualServer
    """

    # CN is required by STRUCTURAL class, but we'll use it as identifier
    cn = models.CharField(
        max_length=255,
        verbose_name="clientIdentifier",
        help_text="Client identifier (IP address or hostname)",
    )

    # Additional RADIUS client attributes
    radius_client_secret = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="radiusClientSecret",
        help_text="Shared secret between client and server",
    )
    radius_client_shortname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="radiusClientShortname",
        help_text="Short name for the client",
    )
    radius_client_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="radiusClientType",
        help_text="Type of client (e.g., 'cisco', 'linux')",
    )
    radius_client_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="radiusClientComment",
        help_text="Additional comments about this client",
    )
    radius_client_virtual_server = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="radiusClientVirtualServer",
        help_text="Virtual server to use for this client",
    )

    # Standard attributes
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the RADIUS client",
    )
    ou = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalUnit",
        help_text="Organizational unit containing this client",
    )

    ldap_base_dn = settings.LDAP_OU_RADIUS + "," + settings.LDAP_BASE_DN
    object_classes = ["radiusObjectProfile"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'radius_client_secret': 'radiusClientSecret',
        'radius_client_shortname': 'radiusClientShortname',
        'radius_client_type': 'radiusClientType',
        'radius_client_comment': 'radiusClientComment',
        'radius_client_virtual_server': 'radiusClientVirtualServer',
        'description': 'description',
        'ou': 'ou',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_radius_clients"
        verbose_name = "RADIUS Client"
        verbose_name_plural = "RADIUS Clients"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this RADIUS client."""
        from ..utils.dn import build_radius_dn

        return build_radius_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
