"""
LDAP models for Sendmail schema.

This module provides:
- SendmailMTA: MTA server configuration
- SendmailMapEntry: Map/alias entries (aliases, transport maps)
"""

from typing import List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class SendmailMTA(LDAPModel):
    """Sendmail MTA server configuration.

    Based on sendmail.schema sendmailMTA.
    STRUCTURAL object class.

    MAY: sendmailMTACluster, sendmailMTAHost, Description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="mtaName",
        help_text="MTA server name",
    )
    sendmail_mta_cluster = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="sendmailMTACluster",
        help_text="Cluster name for this MTA",
    )
    sendmail_mta_host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="sendmailMTAHost",
        help_text="Hostname of this MTA server",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this MTA server",
    )

    ldap_base_dn = settings.LDAP_OU_SENDMAIL + "," + settings.LDAP_BASE_DN
    object_classes = ["sendmailMTA"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'sendmail_mta_cluster': 'sendmailMTACluster',
        'sendmail_mta_host': 'sendmailMTAHost',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_sendmail_mta"
        verbose_name = "Sendmail MTA"
        verbose_name_plural = "Sendmail MTAs"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this MTA."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_SENDMAIL)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class SendmailMapEntry(LDAPModel):
    """Sendmail map entry (alias, transport, etc.).

    Based on sendmail.schema sendmailMTAMapObject and sendmailMTAAliasObject.
    STRUCTURAL object class.

    MUST: cn, sendmailMTAKey
    MAY: sendmailMTAMapName, sendmailMTAMapValue,
         sendmailMTAMapSearch, sendmailMTACluster, sendmailMTAHost
    """

    # Map type selector
    MAP_TYPES = [
        ("aliases", "Aliases"),
        ("transport", "Transport Maps"),
        ("generic", "Generic Maps"),
        ("relay", "Relay Maps"),
        ("access", "Access Maps"),
        ("domains", "Domains"),
        ("virtual", "Virtual Domains"),
    ]

    cn = models.CharField(
        max_length=255,
        verbose_name="entryName",
        help_text="Entry identifier",
    )
    sendmail_mta_map_name = models.CharField(
        max_length=100,
        choices=MAP_TYPES,
        verbose_name="sendmailMTAMapName",
        help_text="Map type (aliases, transport, etc.)",
    )
    sendmail_mta_key = models.CharField(
        max_length=255,
        verbose_name="sendmailMTAKey",
        help_text="Key (left side of map entry)",
    )
    sendmail_mta_map_value = models.TextField(
        verbose_name="sendmailMTAMapValue",
        help_text="Value (right side of map entry)",
    )
    sendmail_mta_map_search = models.BooleanField(
        default=False,
        verbose_name="sendmailMTAMapSearch",
        help_text="Recursive search flag",
    )

    # MTA reference
    mta_server = models.ForeignKey(
        "SendmailMTA",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="map_entries",
        help_text="Associated MTA server",
    )

    ldap_base_dn = settings.LDAP_OU_SENDMAIL + "," + settings.LDAP_BASE_DN
    object_classes = ["sendmailMTAMapObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'sendmail_mta_map_name': 'sendmailMTAMapName',
        'sendmail_mta_key': 'sendmailMTAKey',
        'sendmail_mta_map_value': 'sendmailMTAMapValue',
        'sendmail_mta_map_search': 'sendmailMTAMapSearch',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_sendmail_map_entries"
        verbose_name = "Sendmail Map Entry"
        verbose_name_plural = "Sendmail Map Entries"

    def __str__(self) -> str:
        return f"{self.sendmail_mta_key} -> {self.sendmail_mta_map_value}"

    @property
    def dn(self) -> str:
        """Get the DN for this map entry."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_SENDMAIL)
        # Map name becomes part of DN to organize entries
        map_name = self.sendmail_mta_map_name.replace("-", "_")
        return f"cn={map_name},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
