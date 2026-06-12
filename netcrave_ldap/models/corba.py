"""
LDAP models for OpenLDAP CORBA schema.

This module provides:
- corbaContainer: Container for a CORBA object (STRUCTURAL)
- corbaObject: Abstract base class for CORBA objects
- corbaObjectReference: Auxiliary class for CORBA interoperable object references
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class CorbaContainer(LDAPModel):
    """CORBA Container.

    Based on corba.schema corbaContainer.
    STRUCTURAL object class.

    MUST: cn
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="containerName",
        help_text="Container name (cn)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this CORBA container",
    )

    ldap_base_dn = settings.LDAP_OU_CORBA + "," + settings.LDAP_BASE_DN
    object_classes = ["corbaContainer"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_corba_container"
        verbose_name = "CORBA Container"
        verbose_name_plural = "CORBA Containers"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this CORBA container."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CORBA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class CorbaObject(LDAPModel):
    """CORBA Object (abstract base).

    Based on corba.schema corbaObject.
    ABSTRACT object class.

    MAY: corbaRepositoryId, description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="objectName",
        help_text="Object name (cn)",
    )
    corba_repository_id = models.JSONField(
        blank=True,
        default=list,
        verbose_name="corbaRepositoryId",
        help_text="List of CORBA repository IDs (type IDs)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this CORBA object",
    )

    ldap_base_dn = settings.LDAP_OU_CORBA + "," + settings.LDAP_BASE_DN
    object_classes = ["corbaObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'corba_repository_id': 'corbaRepositoryId',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_corba_object"
        verbose_name = "CORBA Object"
        verbose_name_plural = "CORBA Objects"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this CORBA object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CORBA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class CorbaObjectReference(LDAPModel):
    """CORBA Object Reference (AUXILIARY).

    Based on corba.schema corbaObjectReference.
    AUXILIARY object class.

    MUST: corbaIor
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="referenceName",
        help_text="Reference name (cn)",
    )
    corba_ior = models.TextField(
        verbose_name="corbaIor",
        help_text="Stringified interoperable object reference",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this CORBA object reference",
    )

    ldap_base_dn = settings.LDAP_OU_CORBA + "," + settings.LDAP_BASE_DN
    object_classes = ["corbaObjectReference"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'corba_ior': 'corbaIor',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_corba_reference"
        verbose_name = "CORBA Object Reference"
        verbose_name_plural = "CORBA Object References"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this CORBA object reference."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CORBA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
