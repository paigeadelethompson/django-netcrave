"""
LDAP models for ldapns schema.

This module provides:
- authorizedServiceObject: GSS-API authorized service (AUXILIARY)
- hostObject: Host attribute support (AUXILIARY)
- loginStatusObject: Login status tracking (AUXILIARY)
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class AuthorizedServiceObject(LDAPModel):
    """GSS-API authorized service object.

    Based on ldapns.schema authorizedServiceObject.
    AUXILIARY object class.

    MAY: authorizedService
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="serviceName",
        help_text="Service name (cn)",
    )
    authorized_service = models.JSONField(
        blank=True,
        default=list,
        verbose_name="authorizedService",
        help_text="List of GSS-API authorized service names",
    )

    ldap_base_dn = settings.LDAP_OU_SERVICES + "," + settings.LDAP_BASE_DN
    object_classes = ["authorizedServiceObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'authorized_service': 'authorizedService',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_authorized_service_object"
        verbose_name = "Authorized Service Object"
        verbose_name_plural = "Authorized Service Objects"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this authorized service object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_SERVICES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class HostObject(LDAPModel):
    """Host attribute support object.

    Based on ldapns.schema hostObject.
    AUXILIARY object class.

    MAY: host
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="hostName",
        help_text="Host name (cn)",
    )
    host = models.JSONField(
        blank=True,
        default=list,
        verbose_name="host",
        help_text="List of hostnames or IP addresses",
    )

    ldap_base_dn = settings.LDAP_OU_HOSTS + "," + settings.LDAP_BASE_DN
    object_classes = ["hostObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'host': 'host',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_host_object"
        verbose_name = "Host Object"
        verbose_name_plural = "Host Objects"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this host object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_HOSTS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class LoginStatusObject(LDAPModel):
    """Login status tracking object.

    Based on ldapns.schema loginStatusObject.
    AUXILIARY object class.

    MAY: loginStatus
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="loginName",
        help_text="Login name (cn)",
    )
    login_status = models.JSONField(
        blank=True,
        default=list,
        verbose_name="loginStatus",
        help_text="List of currently logged in sessions",
    )

    ldap_base_dn = settings.LDAP_OU_USERS + "," + settings.LDAP_BASE_DN
    object_classes = ["loginStatusObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'login_status': 'loginStatus',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_login_status_object"
        verbose_name = "Login Status Object"
        verbose_name_plural = "Login Status Objects"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this login status object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_USERS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
