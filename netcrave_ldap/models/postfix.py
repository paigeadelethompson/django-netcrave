"""
LDAP models for Postfix mail server.

This module provides:
- PostfixAlias: Mail aliases (similar to Sendmail)
- PostfixTransport: Transport maps for routing
"""

from typing import List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class PostfixAlias(LDAPModel):
    """Postfix mail alias entry.

    Uses standard inetOrgPerson/mailRoutingAddress attributes.
    """

    # Mail recipient (destination)
    mail = models.EmailField(
        help_text="Destination email address",
    )
    destination = models.JSONField(
        help_text="List of source addresses that map to this destination",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Alias description",
    )

    ldap_base_dn = settings.LDAP_OU_POSTFIX + "," + settings.LDAP_BASE_DN
    object_classes = ["top"]

    ldap_attributes_map: Dict[str, str] = {
        'mail': 'mail',
        'destination': 'mailAliasDestination',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_postfix_aliases"
        verbose_name = "Postfix Alias"
        verbose_name_plural = "Postfix Aliases"

    def __str__(self) -> str:
        return f"{', '.join(self.destination)} -> {self.mail}"

    @property
    def dn(self) -> str:
        """Get the DN for this alias."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_POSTFIX)
        # Use mail as RDN
        mail_part = self.mail.replace("@", ".")
        return f"mail={mail_part},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class PostfixTransport(LDAPModel):
    """Postfix transport map entry.

    For routing mail to specific hosts or services.
    """

    mail_routing_domain = models.CharField(
        max_length=255,
        verbose_name="mailRoutingDomain",
        help_text="Domain pattern (e.g., example.com, *.example.com)",
    )
    transport_type = models.CharField(
        max_length=50,
        choices=[
            ("smtp", "SMTP"),
            ("local", "Local delivery"),
            ("virtual", "Virtual delivery"),
            ("relay", "Relay via another host"),
            ("dovecot", "Dovecot LMTP"),
            ("lmtp", "LMTP"),
        ],
        verbose_name="Transport Type",
    )
    transport_next_hop = models.CharField(
        max_length=255,
        verbose_name="Next Hop",
        help_text="Destination (host, :port, or special target)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Transport map description",
    )

    ldap_base_dn = settings.LDAP_OU_POSTFIX + "," + settings.LDAP_BASE_DN
    object_classes = ["top"]

    ldap_attributes_map: Dict[str, str] = {
        'mail_routing_domain': 'mailRoutingDomain',
        'transport_type': 'transportType',
        'transport_next_hop': 'transportNextHop',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_postfix_transports"
        verbose_name = "Postfix Transport Map"
        verbose_name_plural = "Postfix Transport Maps"

    def __str__(self) -> str:
        return f"{self.mail_routing_domain} via {self.transport_type}"

    @property
    def dn(self) -> str:
        """Get the DN for this transport."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_POSTFIX)
        # Use domain as RDN (convert to safe format)
        domain_part = self.mail_routing_domain.replace(".", ".dc=").replace("@", "")
        return f"domain={self.mail_routing_domain},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
