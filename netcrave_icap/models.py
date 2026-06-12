"""LDAP models for netcrave_icap."""

from typing import List

from django.conf import settings
from django.db import models

# Import LDAPModel from netcrave_ldap since we're using the same pattern
try:
    from netcrave_ldap.models.base import LDAPModel
except ImportError:
    # Fallback if netcrave_ldap is not available during early imports
    class LDAPModel(models.Model):
        """Abstract base model for LDAP-backed models."""
        ldap_base_dn: str = ""
        object_classes: List[str] = []
        class Meta:
            abstract = True

        def __str__(self) -> str:
            return self.get_dn()

        @property
        def dn(self) -> str:
            raise NotImplementedError("Subclasses must implement dn property")

        def get_dn(self) -> str:
            return self.dn

        @classmethod
        def get_base_dn(cls) -> str:
            if cls.ldap_base_dn:
                return cls.ldap_base_dn
            raise NotImplementedError("Subclasses must implement ldap_base_dn or get_base_dn()")

        @classmethod
        def get_object_classes(cls) -> List[str]:
            return cls.object_classes.copy()

        def get_ldap_attributes(self) -> dict:
            return {}

        def save(self, *args: any, **kwargs: any) -> None:
            self.full_clean()
            super().save(*args, **kwargs)


class ICAPUserProfile(LDAPModel):
    """ICAP user access control stored in LDAP.

    Based on the netcrave-icap.schema definition.
    AUXILIARY object class - should be added to existing users.

    MAY:
        icapAllowICAPAccess - Whether user can use ICAP
        icapMaxConnections - Max connections for this user
    """

    # These fields map to LDAP attributes in the icapUser auxiliary object class
    allow_icap_access = models.BooleanField(
        default=True,
        verbose_name="Allow ICAP Access",
        help_text="Whether this user is allowed to use the ICAP service",
    )

    max_connections = models.PositiveIntegerField(
        default=10,
        verbose_name="Max Connections",
        help_text="Maximum concurrent ICAP connections allowed",
    )

    ldap_base_dn = settings.LDAP_BASE_DN
    object_classes = ["icapUser"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_icap_user_profiles"
        verbose_name = "ICAP User Profile"
        verbose_name_plural = "ICAP User Profiles"

    def __str__(self) -> str:
        return f"ICAP Profile for {self.dn}"


class ICAPService(LDAPModel):
    """ICAP service configuration stored in LDAP.

    Based on the netcrave-icap.schema definition.
    STRUCTURAL object class.

    MUST:
        cn - Service name (hostname)
        icapServiceHost - Host address
        icapServicePort - Port number

    MAY:
        icapServiceName - Display name
        icapMaxBodySize - Maximum body size
        icapPreviewSize - Preview size for request modification
        icapMethodsSupported - Supported methods (REQMOD, RESPMOD, OPTIONS)
        icapAuthenticationType - Auth type (Kerberos, Basic, None)
        icapKerberosServicePrincipal - Kerberos principal
        icapKerberosKeytab - Keytab file path
        icapAllowAnonymous - Allow anonymous access
        icapMaxConnections - Max concurrent connections
        icapTransferComplete - Require complete transfer
        description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="serviceHost",
        help_text="ICAP service hostname (cn)",
    )
    icap_service_host = models.CharField(
        max_length=255,
        verbose_name="icapServiceHost",
        help_text="IP address or hostname of the ICAP server",
    )
    icap_service_port = models.PositiveIntegerField(
        default=1344,
        verbose_name="icapServicePort",
        help_text="TCP port number (default: 1344)",
    )

    # Optional attributes
    icap_service_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="icapServiceName",
        help_text="Display name for the ICAP service",
    )
    icap_max_body_size = models.PositiveIntegerField(
        default=0,
        verbose_name="icapMaxBodySize",
        help_text="Maximum body size in bytes (0 = unlimited)",
    )
    icap_preview_size = models.PositiveIntegerField(
        default=1024,
        verbose_name="icapPreviewSize",
        help_text="Preview size for request modification",
    )
    icap_methods_supported = models.JSONField(
        blank=True,
        default=list,
        verbose_name="icapMethodsSupported",
        help_text="List of supported methods: REQMOD, RESPMOD, OPTIONS",
    )
    icap_authentication_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="icapAuthenticationType",
        help_text="Authentication type: Kerberos, Basic, or None",
    )
    icap_kerberos_service_principal = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="icapKerberosServicePrincipal",
        help_text="Kerberos service principal (e.g., HTTP/squid@EXAMPLE.COM)",
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
        help_text="Allow anonymous ICAP access",
    )
    icap_max_connections = models.PositiveIntegerField(
        default=100,
        verbose_name="icapMaxConnections",
        help_text="Maximum concurrent connections",
    )
    icap_transfer_complete = models.BooleanField(
        default=True,
        verbose_name="icapTransferComplete",
        help_text="Require complete transfer mode",
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="ICAP service description",
    )

    ldap_base_dn = getattr(settings, "LDAP_OU_ICAP", "ou=icap") + "," + settings.LDAP_BASE_DN
    object_classes = ["icapService"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_icap_services"
        verbose_name = "ICAP Service"
        verbose_name_plural = "ICAP Services"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this ICAP service."""
        from netcrave_ldap.utils.dn import build_icap_dn
        return build_icap_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def get_ldap_attributes(self) -> dict:
        """Get LDAP attributes for this entry."""
        attrs = {
            "objectClass": self.object_classes,
            "cn": [self.cn],
            "icapServiceHost": [self.icap_service_host],
            "icapServicePort": [str(self.icap_service_port)],
        }

        if self.icap_service_name:
            attrs["icapServiceName"] = [self.icap_service_name]
        if self.icap_max_body_size > 0:
            attrs["icapMaxBodySize"] = [str(self.icap_max_body_size)]
        attrs["icapPreviewSize"] = [str(self.icap_preview_size)]

        if self.icap_methods_supported:
            attrs["icapMethodsSupported"] = list(self.icap_methods_supported)
        else:
            attrs["icapMethodsSupported"] = ["REQMOD", "RESPMOD", "OPTIONS"]

        if self.icap_authentication_type:
            attrs["icapAuthenticationType"] = [self.icap_authentication_type]
        if self.icap_kerberos_service_principal:
            attrs["icapKerberosServicePrincipal"] = [self.icap_kerberos_service_principal]
        if self.icap_kerberos_keytab:
            attrs["icapKerberosKeytab"] = [self.icap_kerberos_keytab]

        attrs["icapAllowAnonymous"] = ["TRUE" if self.icap_allow_anonymous else "FALSE"]
        attrs["icapMaxConnections"] = [str(self.icap_max_connections)]
        attrs["icapTransferComplete"] = ["TRUE" if self.icap_transfer_complete else "FALSE"]

        if self.description:
            attrs["description"] = [self.description]

        return attrs
