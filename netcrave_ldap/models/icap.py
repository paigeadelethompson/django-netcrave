"""
LDAP models for Netcrave ICAP schema.

This module provides:
- icapService: ICAP service configuration (STRUCTURAL)
- icapUser: ICAP user access control (AUXILIARY)
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class IcapService(LDAPModel):
    """Netcrave ICAP service configuration.

    Based on netcrave-icap.schema icapService object class.
    STRUCTURAL object class.

    MUST: cn, icapServiceHost, icapServicePort
    MAY: icapServiceName, icapMaxBodySize, icapPreviewSize,
         icapMethodsSupported, icapAuthenticationType,
         icapKerberosServicePrincipal, icapKerberosKeytab,
         icapAllowAnonymous, icapMaxConnections, icapTransferComplete,
         icapRequestHeaders, icapResponseHeaders, icapAllowHeaders,
         description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="serviceName",
        help_text="ICAP service name (cn)",
    )
    icap_service_host = models.CharField(
        max_length=255,
        verbose_name="icapServiceHost",
        help_text="Host address of the ICAP service",
    )
    icap_service_port = models.PositiveIntegerField(
        verbose_name="icapServicePort",
        help_text="Port number of the ICAP service",
    )
    icap_service_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="icapServiceName",
        help_text="Name of the ICAP service",
    )
    icap_max_body_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="icapMaxBodySize",
        help_text="Maximum body size supported by ICAP service",
    )
    icap_preview_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="icapPreviewSize",
        help_text="Preview size for request modification",
    )
    icap_methods_supported = models.JSONField(
        blank=True,
        default=list,
        verbose_name="icapMethodsSupported",
        help_text="List of supported ICAP methods",
    )
    icap_authentication_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="icapAuthenticationType",
        help_text="Authentication type required by ICAP service",
    )
    icap_kerberos_service_principal = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="icapKerberosServicePrincipal",
        help_text="Kerberos service principal for ICAP authentication",
    )
    icap_kerberos_keytab = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="icapKerberosKeytab",
        help_text="Path to Kerberos keytab file",
    )
    icap_allow_anonymous = models.BooleanField(
        default=False,
        verbose_name="icapAllowAnonymous",
        help_text="Whether anonymous ICAP access is allowed",
    )
    icap_max_connections = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="icapMaxConnections",
        help_text="Maximum concurrent connections allowed",
    )
    icap_transfer_complete = models.BooleanField(
        default=False,
        verbose_name="icapTransferComplete",
        help_text="Whether complete transfer is required",
    )
    icap_request_headers = models.JSONField(
        blank=True,
        default=list,
        verbose_name="icapRequestHeaders",
        help_text="Request headers to pass to ICAP service",
    )
    icap_response_headers = models.JSONField(
        blank=True,
        default=list,
        verbose_name="icapResponseHeaders",
        help_text="Response headers to pass from ICAP service",
    )
    icap_allow_headers = models.JSONField(
        blank=True,
        default=list,
        verbose_name="icapAllowHeaders",
        help_text="Additional headers to allow in requests",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this ICAP service",
    )

    ldap_base_dn = settings.LDAP_OU_ICAP + "," + settings.LDAP_BASE_DN
    object_classes = ["icapService"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'icap_service_host': 'icapServiceHost',
        'icap_service_port': 'icapServicePort',
        'icap_service_name': 'icapServiceName',
        'icap_max_body_size': 'icapMaxBodySize',
        'icap_preview_size': 'icapPreviewSize',
        'icap_methods_supported': 'icapMethodsSupported',
        'icap_authentication_type': 'icapAuthenticationType',
        'icap_kerberos_service_principal': 'icapKerberosServicePrincipal',
        'icap_kerberos_keytab': 'icapKerberosKeytab',
        'icap_allow_anonymous': 'icapAllowAnonymous',
        'icap_max_connections': 'icapMaxConnections',
        'icap_transfer_complete': 'icapTransferComplete',
        'icap_request_headers': 'icapRequestHeaders',
        'icap_response_headers': 'iapResponseHeaders',
        'icap_allow_headers': 'iapAllowHeaders',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_icap_service"
        verbose_name = "ICAP Service"
        verbose_name_plural = "ICAP Services"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this ICAP service."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_ICAP)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class IcapUser(LDAPModel):
    """Netcrave ICAP user access control.

    Based on netcrave-icap.schema icapUser object class.
    AUXILIARY object class.

    MAY: icapAllowICAPAccess, icapMaxConnectionsPerUser
    """

    # Use a OneToOne relationship to link with auth.User or similar
    # For simplicity, we use cn as identifier and rely on external reference

    cn = models.CharField(
        max_length=255,
        verbose_name="userName",
        help_text="User name (cn) for ICAP access control",
    )
    icap_allow_icap_access = models.BooleanField(
        default=True,
        verbose_name="icapAllowICAPAccess",
        help_text="Whether a user is allowed to use ICAP service",
    )
    icap_max_connections_per_user = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="icapMaxConnectionsPerUser",
        help_text="Maximum concurrent connections for a specific user",
    )

    ldap_base_dn = settings.LDAP_OU_USERS + "," + settings.LDAP_BASE_DN
    object_classes = ["icapUser"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'icap_allow_icap_access': 'iapAllowICAPAccess',
        'icap_max_connections_per_user': 'iapMaxConnectionsPerUser',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_icap_user"
        verbose_name = "ICAP User"
        verbose_name_plural = "ICAP Users"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this ICAP user."""
        from ..utils.dn import build_user_dn

        return build_user_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
