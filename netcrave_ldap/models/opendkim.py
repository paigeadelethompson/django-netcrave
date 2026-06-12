"""
LDAP models for OpenDKIM schema.

This module provides:
- DKIM: DKIM selector and key container (AUXILIARY)
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class DKIM(LDAPModel):
    """OpenDKIM DKIM selector and key container.

    Based on opendkim.schema DKIM object class.
    AUXILIARY object class.

    MUST: DKIMSelector, DKIMKey
    MAY: DKIMIdentity, DKIMDomain
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="selectorName",
        help_text="DKIM selector name (used as DNS record name)",
    )
    dkim_selector = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="DKIMSelector",
        help_text="Selector name associated with DKIM signing key",
    )
    dkim_key = models.TextField(
        verbose_name="DKIMKey",
        help_text="DKIM signing key (PEM format or path to key file)",
    )
    dkim_identity = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="DKIMIdentity",
        help_text="The Agent or User Identifier (AUID)",
    )
    dkim_domain = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="DKIMDomain",
        help_text="DKIM sender domain",
    )

    ldap_base_dn = settings.LDAP_OU_DKIM + "," + settings.LDAP_BASE_DN
    object_classes = ["DKIM"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'dkim_selector': 'DKIMSelector',
        'dkim_key': 'DKIMKey',
        'dkim_identity': 'DKIMIdentity',
        'dkim_domain': 'DKIMDomain',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_opendkim"
        verbose_name = "OpenDKIM"
        verbose_name_plural = "OpenDKIM Records"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this DKIM record."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_DKIM)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
