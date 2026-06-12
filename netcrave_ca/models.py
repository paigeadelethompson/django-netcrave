"""LDAP models for netcrave_ca - Certificate management via LDAP."""

import fnmatch
from datetime import timezone
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


class CertificateTemplate(LDAPModel):
    """Certificate template for defining certificate properties.

    Stores configuration in LDAP under ou=pki,ou=certificates,dc=example,dc=com
    Using netcrave-certificate.schema's certificateTemplate object class.
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="Template Name",
        help_text="Name of this certificate template (cn)",
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this template is used for",
    )

    # Certificate properties
    validity_days = models.PositiveIntegerField(
        default=365,
        verbose_name="Validity (days)",
        help_text="Certificate validity period in days",
    )
    key_size = models.PositiveIntegerField(
        default=2048,
        choices=[
            (1024, "1024 bits"),
            (2048, "2048 bits"),
            (3072, "3072 bits"),
            (4096, "4096 bits"),
        ],
        verbose_name="RSA Key Size",
        help_text="Size of the RSA key to generate",
    )

    # Key Usage (RFC 5280)
    usage_key_cert_sign = models.BooleanField(
        default=False,
        verbose_name="Key Certificate Sign",
        help_text="If true, certificate can sign other certificates",
    )
    usage_crl_sign = models.BooleanField(
        default=False,
        verbose_name="Key CRL Sign",
        help_text="If true, certificate can sign CRLs",
    )
    usage_key_encipherment = models.BooleanField(
        default=True,
        verbose_name="Key Encipherment",
        help_text="If true, key can be used for encipherment",
    )
    usage_key_data_sign = models.BooleanField(
        default=False,
        verbose_name="Key Data Signature",
        help_text="If true, key can be used for digital signatures",
    )

    # Extended Key Usage (RFC 5280)
    usage_server_auth = models.BooleanField(
        default=False,
        verbose_name="Server Authentication",
        help_text="If true, certificate can be used for TLS server auth",
    )
    usage_client_auth = models.BooleanField(
        default=False,
        verbose_name="Client Authentication",
        help_text="If true, certificate can be used for TLS client auth",
    )
    usage_code_signing = models.BooleanField(
        default=False,
        verbose_name="Code Signing",
        help_text="If true, certificate can be used for code signing",
    )
    usage_email_protection = models.BooleanField(
        default=False,
        verbose_name="Email Protection",
        help_text="If true, certificate can be used for email protection",
    )

    # Subject Alternative Names
    san_dns_pattern = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="SAN DNS Pattern",
        help_text="Pattern for DNS SANs (e.g., '*.example.com' or specific names)",
    )
    san_ip_pattern = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="SAN IP Pattern",
        help_text="Pattern for IP address SANs",
    )

    # Is this the default template?
    is_default = models.BooleanField(
        default=False,
        verbose_name="Is Default Template",
        help_text="If true, this template will be used as default when no match is found",
    )

    ldap_base_dn = getattr(settings, "LDAP_OU_PKI", "ou=pki") + "," + \
                   getattr(settings, "LDAP_OU_CERTIFICATES", "ou=certificates") + "," + \
                   settings.LDAP_BASE_DN
    object_classes = ["certificateTemplate"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_certificate_templates"
        verbose_name = "Certificate Template"
        verbose_name_plural = "Certificate Templates"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this template."""
        from netcrave_ldap.utils.dn import build_computer_dn  # Use computer_dn as it uses cn
        return f"cn={self.cn},{self.ldap_base_dn}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def get_ldap_attributes(self) -> dict:
        """Get LDAP attributes for this entry."""
        attrs = {
            "objectClass": self.object_classes,
            "cn": [self.cn],
        }

        if self.description:
            attrs["description"] = [self.description]

        attrs["certificateValidityDays"] = [str(self.validity_days)]
        attrs["certificateKeySize"] = [str(self.key_size)]

        if self.san_dns_pattern:
            attrs["certificateSANPattern"] = [self.san_dns_pattern]

        # Boolean attributes
        if self.usage_key_cert_sign:
            attrs["certificateUsageServerAuth"] = ["TRUE"]
        else:
            attrs["certificateUsageServerAuth"] = ["FALSE"]

        if self.usage_server_auth:
            attrs["certificateUsageServerAuth"] = ["TRUE"]
        else:
            attrs["certificateUsageServerAuth"] = ["FALSE"]

        if self.usage_client_auth:
            attrs["certificateUsageClientAuth"] = ["TRUE"]
        else:
            attrs["certificateUsageClientAuth"] = ["FALSE"]

        if self.usage_email_protection:
            attrs["certificateUsageEmailProtection"] = ["TRUE"]
        else:
            attrs["certificateUsageEmailProtection"] = ["FALSE"]

        if self.usage_code_signing:
            attrs["certificateUsageCodeSigning"] = ["TRUE"]
        else:
            attrs["certificateUsageCodeSigning"] = ["FALSE"]

        return attrs


class CertificateProfile(LDAPModel):
    """Certificate profile that maps hostnames to templates for ACME.

    Profiles are used by ACME to determine which template to use
    when a certificate request is made for a specific hostname.
    Uses the certificateProfile object class from netcrave-certificate.schema.
    """

    cn = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Profile Name",
        help_text="Name of this certificate profile (cn)",
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this profile is used for",
    )

    # The template to apply - stored as cn reference
    template_cn = models.CharField(
        max_length=255,
        verbose_name="Template Name",
        help_text="Name of the certificate template to use",
    )

    # Hostname matching - stores list of hostnames/patterns
    hostname_patterns = models.JSONField(
        default=list,
        verbose_name="Hostname Patterns",
        help_text="List of hostnames or patterns (wildcards supported)",
    )

    # Kerberos access control for ACME
    require_kerberos_auth = models.BooleanField(
        default=True,
        verbose_name="Require Kerberos Auth",
        help_text="If true, requires Kerberos authentication via ACME",
    )
    allowed_principals = models.JSONField(
        blank=True,
        default=list,
        verbose_name="Allowed Principals",
        help_text="List of specific Kerberos principals allowed (empty = all)",
    )

    # ACME-specific settings
    auto_renewal_days = models.PositiveIntegerField(
        default=30,
        verbose_name="Auto-renewal Window",
        help_text="Days before expiration to trigger renewal notification",
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name="Enabled",
        help_text="If false, this profile will not be used by ACME",
    )

    ldap_base_dn = getattr(settings, "LDAP_OU_PKI", "ou=pki") + "," + \
                   getattr(settings, "LDAP_OU_CERTIFICATES", "ou=certificates") + "," + \
                   settings.LDAP_BASE_DN
    object_classes = ["certificateProfile"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_certificate_profiles"
        verbose_name = "Certificate Profile"
        verbose_name_plural = "Certificate Profiles"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this profile."""
        return f"cn={self.cn},{self.ldap_base_dn}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def matches_hostname(self, hostname: str) -> bool:
        """Check if this profile matches the given hostname."""
        import fnmatch

        for pattern in self.hostname_patterns:
            if fnmatch.fnmatch(hostname, pattern):
                return True
        return False

    def get_ldap_attributes(self) -> dict:
        """Get LDAP attributes for this entry."""
        attrs = {
            "objectClass": self.object_classes,
            "cn": [self.cn],
        }

        if self.description:
            attrs["description"] = [self.description]

        attrs["certificateTemplate"] = [self.template_cn]
        attrs["certificateHostnames"] = list(self.hostname_patterns)

        attrs["certificateRequireKerberos"] = ["TRUE" if self.require_kerberos_auth else "FALSE"]
        attrs["certificateAutoRenewalDays"] = [str(self.auto_renewal_days)]
        attrs["certificateTemplateEnabled"] = ["TRUE" if self.enabled else "FALSE"]

        return attrs


class CertificateRecord(LDAPModel):
    """Certificate record storing metadata about issued certificates.

    This model stores metadata in LDAP, NOT the actual certificate data.
    Certificate files should be stored in a secure external system
    (file system, secrets manager, etc.).
    Uses the certificateRecord object class from netcrave-certificate.schema.
    """

    STATUS_CHOICES = [
        ("valid", "Valid"),
        ("revoked", "Revoked"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    cn = models.CharField(
        max_length=255,
        verbose_name="Subject CN",
        help_text="Common Name from certificate subject (cn)",
    )
    serial_number = models.CharField(
        max_length=64,
        verbose_name="Serial Number",
        help_text="Certificate serial number (hex format)",
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="valid",
        verbose_name="Status",
        help_text="Current certificate status",
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Revoked At",
        help_text="When the certificate was revoked",
    )

    # Validity period
    not_before = models.DateTimeField(verbose_name="Not Before")
    not_after = models.DateTimeField(verbose_name="Not After")

    # Issuer information
    issuer_cn = models.CharField(
        max_length=255,
        verbose_name="Issuer CN",
        help_text="Common Name of the issuing CA",
    )

    # Profile/template references (stored as cn)
    profile_cn = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Profile Name",
        help_text="Name of the certificate profile used",
    )
    template_cn = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Template Name",
        help_text="Name of the certificate template used",
    )

    # Kerberos auth tracking
    auth_principal = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Authorization Principal",
        help_text="Kerberos principal that authorized this certificate request",
    )
    revocation_reason = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Revocation Reason",
        help_text="Reason for certificate revocation",
    )

    # Storage locations (external system pointers)
    storage_path = models.CharField(
        max_length=512,
        blank=True,
        verbose_name="Certificate Path",
        help_text="Path to where the certificate is stored (external)",
    )
    private_key_path = models.CharField(
        max_length=512,
        blank=True,
        verbose_name="Private Key Path",
        help_text="Path to where the private key is stored (external)",
    )

    # ACME association
    acme_order_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ACME Order ID",
        help_text="ID of the ACME order that issued this certificate",
    )

    ldap_base_dn = getattr(settings, "LDAP_OU_PKI", "ou=pki") + "," + \
                   getattr(settings, "LDAP_OU_CERTIFICATES", "ou=certificates") + "," + \
                   settings.LDAP_BASE_DN
    object_classes = ["certificateRecord"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_certificate_records"
        verbose_name = "Certificate Record"
        verbose_name_plural = "Certificate Records"

    def __str__(self) -> str:
        return f"{self.cn} ({self.serial_number})"

    @property
    def dn(self) -> str:
        """Get the DN for this certificate record."""
        # Use serial number to make DNs unique
        safe_serial = self.serial_number.replace(":", "")
        return f"cn={safe_serial},{self.ldap_base_dn}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def get_ldap_attributes(self) -> dict:
        """Get LDAP attributes for this entry."""
        attrs = {
            "objectClass": self.object_classes,
            "cn": [self.cn],
            "certificateSerialNumber": [self.serial_number],
        }

        if self.description:
            attrs["description"] = [self.description]

        attrs["certificateSubjectCN"] = [self.cn]
        attrs["certificateIssuerCN"] = [self.issuer_cn]
        attrs["certificateStatus"] = [self.status]

        # Convert datetime to LDAP generalized time format
        from datetime import timezone

        def to_ldap_time(dt):
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y%m%d%H%M%SZ")

        attrs["certificateNotBefore"] = [to_ldap_time(self.not_before)]
        attrs["certificateNotAfter"] = [to_ldap_time(self.not_after)]

        if self.profile_cn:
            attrs["certificateProfile"] = [self.profile_cn]
        if self.template_cn:
            attrs["certificateTemplate"] = [self.template_cn]

        if self.auth_principal:
            attrs["certificateAuthPrincipal"] = [self.auth_principal]

        if self.revoked_at:
            attrs["certificateRevokedAt"] = [to_ldap_time(self.revoked_at)]
        if self.revocation_reason:
            attrs["certificateRevocationReason"] = [self.revocation_reason]

        if self.storage_path:
            attrs["certificateStoragePath"] = [self.storage_path]
        if self.private_key_path:
            attrs["certificatePrivateKeyPath"] = [self.private_key_path]

        if self.acme_order_id:
            attrs["acmeOrderID"] = [self.acme_order_id]

        return attrs
