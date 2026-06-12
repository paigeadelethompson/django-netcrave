"""
LDAP models for NIS schema attributes.

This module provides:
- NisObject: General NIS map object model
"""

from typing import List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class NisObject(LDAPModel):
    """NIS map object model.

    Based on nisObject from nis.schema.
    STRUCTURAL object class.

    MUST: cn, nisMapName, nisMapEntry
    MAY: description
    """

    cn = models.CharField(
        max_length=255,
        help_text="Common name (key for the map entry)",
    )
    nis_map_name = models.CharField(
        max_length=255,
        verbose_name="nisMapName",
        help_text="Name of the NIS map this entry belongs to",
    )
    nis_map_entry = models.TextField(
        verbose_name="nisMapEntry",
        help_text="Value of the map entry (left=value format)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this map entry",
    )

    ldap_base_dn = settings.LDAP_OU_GROUPS + "," + settings.LDAP_BASE_DN
    object_classes = ["nisObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'nis_map_name': 'nisMapName',
        'nis_map_entry': 'nisMapEntry',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_nis_objects"
        verbose_name = "NIS Object"
        verbose_name_plural = "NIS Objects"

    def __str__(self) -> str:
        return f"{self.cn} in {self.nis_map_name}"

    @property
    def dn(self) -> str:
        """Get the DN for this NIS object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_GROUPS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
