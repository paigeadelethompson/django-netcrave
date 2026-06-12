"""
LDAP models for Netcrave Certificate schema.

This module provides:
- certificateTemplate: Certificate template configuration (STRUCTURAL)
- certificateProfile: Certificate profile with hostname mapping (STRUCTURAL)
- certificateRecord: Issued certificate metadata (STRUCTURAL)
- certificateAuthority: CA configuration (STRUCTURAL)
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class CertificateTemplate(LDAPModel):
    """Netcrave Certificate Template.

    Based on netcrave-certificate.schema certificateTemplate object class.
    STRUCTURAL object class.

    MUST: cn
    MAY: description, certificateValidityDays, certificateKeySize,
         certificateSANPattern, certificateUsageServerAuth,
         certificateUsageClientAuth, certificateUsageEmailProtection,
         certificateUsageCodeSigning

    Note: Schema appears truncated in the file - implementation based on visible attributes.
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="templateName",
        help_text="Certificate template name (cn)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this certificate template",
    )
    certificate_validity_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="certificateValidityDays",
        help_text="Default validity period for certificates from this template (days)",
    )
    certificate_key_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="certificateKeySize",
        help_text="Default RSA key size for certificates from this template",
    )
    certificate_san_pattern = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificateSANPattern",
        help_text="Pattern for Subject Alternative Names",
    )
    certificate_usage_server_auth = models.BooleanField(
        default=False,
        verbose_name="certificateUsageServerAuth",
        help_text="Certificate can be used for TLS server authentication",
    )
    certificate_usage_client_auth = models.BooleanField(
        default=False,
        verbose_name="certificateUsageClientAuth",
        help_text="Certificate can be used for TLS client authentication",
    )
    certificate_usage_email_protection = models.BooleanField(
        default=False,
        verbose_name="certificateUsageEmailProtection",
        help_text="Certificate can be used for email protection",
    )
    certificate_usage_code_signing = models.BooleanField(
        default=False,
        verbose_name="certificateUsageCodeSigning",
        help_text="Certificate can be used for code signing",
    )

    ldap_base_dn = settings.LDAP_OU_CERTIFICATES + "," + settings.LDAP_BASE_DN
    object_classes = ["certificateTemplate"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'description': 'description',
        'certificate_validity_days': 'certificateValidityDays',
        'certificate_key_size': 'certificateKeySize',
        'certificate_san_pattern': 'certificateSANPattern',
        'certificate_usage_server_auth': 'certificateUsageServerAuth',
        'certificate_usage_client_auth': 'certificateUsageClientAuth',
        'certificate_usage_email_protection': 'certificateUsageEmailProtection',
        'certificate_usage_code_signing': 'certificateUsageCodeSigning',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_certificate_template"
        verbose_name = "Certificate Template"
        verbose_name_plural = "Certificate Templates"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this certificate template."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CERTIFICATES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class CertificateProfile(LDAPModel):
    """Netcrave Certificate Profile.

    Based on netcrave-certificate.schema certificateProfile object class.
    STRUCTURAL object class.

    MUST: cn
    MAY: description, certificateTemplate, certificateHostnames,
         certificateRequireKerberos, certificateAllowedPrincipals,
         certificateAutoRenewalDays

    Note: Schema appears truncated - implementation based on visible attributes.
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="profileName",
        help_text="Certificate profile name (cn)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this certificate profile",
    )
    certificate_template = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificateTemplate",
        help_text="Reference to certificate template",
    )
    certificate_hostnames = models.JSONField(
        blank=True,
        default=list,
        verbose_name="certificateHostnames",
        help_text="List of hostnames covered by this certificate profile",
    )
    certificate_require_kerberos = models.BooleanField(
        default=False,
        verbose_name="certificateRequireKerberos",
        help_text="Whether Kerberos authentication is required for ACME access",
    )
    certificate_allowed_principals = models.JSONField(
        blank=True,
        default=list,
        verbose_name="certificateAllowedPrincipals",
        help_text="List of allowed Kerberos principals for ACME access",
    )
    certificate_auto_renewal_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="certificateAutoRenewalDays",
        help_text="Days before expiration to trigger renewal notification",
    )

    ldap_base_dn = settings.LDAP_OU_CERTIFICATES + "," + settings.LDAP_BASE_DN
    object_classes = ["certificateProfile"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'description': 'description',
        'certificate_template': 'certificateTemplate',
        'certificate_hostnames': 'certificateHostnames',
        'certificate_require_kerberos': 'certificateRequireKerberos',
        'certificate_allowed_principals': 'certificateAllowedPrincipals',
        'certificate_auto_renewal_days': 'certificateAutoRenewalDays',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_certificate_profile"
        verbose_name = "Certificate Profile"
        verbose_name_plural = "Certificate Profiles"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this certificate profile."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CERTIFICATES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class CertificateRecord(LDAPModel):
    """Netcrave Certificate Record.

    Based on netcrave-certificate.schema certificateRecord object class.
    STRUCTURAL object class.

    MUST: cn, certificateSerialNumber
    MAY: certificateSubjectCN, certificateIssuerCN, certificateStatus,
         certificateNotBefore, certificateNotAfter, certificateTemplate,
         certificateProfile, certificateAuthPrincipal, certificateRevokedAt,
         certificateRevocationReason, certificateStoragePath,
         certificatePrivateKeyPath, acmeOrderID

    Note: Schema appears truncated - implementation based on visible attributes.
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="certificateName",
        help_text="Certificate name (cn)",
    )
    certificate_serial_number = models.CharField(
        max_length=64,
        verbose_name="certificateSerialNumber",
        help_text="Certificate serial number in hex format",
    )
    certificate_subject_cn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificateSubjectCN",
        help_text="Common Name from certificate subject",
    )
    certificate_issuer_cn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificateIssuerCN",
        help_text="Common Name of certificate issuer",
    )
    certificate_status = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="certificateStatus",
        help_text="Certificate status (valid, revoked, expired, cancelled)",
    )
    certificate_not_before = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="certificateNotBefore",
        help_text="Certificate validity start time",
    )
    certificate_not_after = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="certificateNotAfter",
        help_text="Certificate validity end time",
    )
    certificate_template = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificateTemplate",
        help_text="Reference to certificate template",
    )
    certificate_profile = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificateProfile",
        help_text="Reference to certificate profile",
    )
    certificate_auth_principal = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificateAuthPrincipal",
        help_text="Kerberos principal that authorized the certificate request",
    )
    certificate_revoked_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="certificateRevokedAt",
        help_text="Time when certificate was revoked",
    )
    certificate_revocation_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="certificateRevocationReason",
        help_text="Reason for certificate revocation",
    )
    certificate_storage_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificateStoragePath",
        help_text="Path to certificate storage (external system)",
    )
    certificate_private_key_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="certificatePrivateKeyPath",
        help_text="Path to private key storage (external system)",
    )
    acme_order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="acmeOrderID",
        help_text="ACME order ID associated with this certificate",
    )

    ldap_base_dn = settings.LDAP_OU_CERTIFICATES + "," + settings.LDAP_BASE_DN
    object_classes = ["certificateRecord"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'certificate_serial_number': 'certificateSerialNumber',
        'certificate_subject_cn': 'certificateSubjectCN',
        'certificate_issuer_cn': 'certificateIssuerCN',
        'certificate_status': 'certificateStatus',
        'certificate_not_before': 'certificateNotBefore',
        'certificate_not_after': 'certificateNotAfter',
        'certificate_template': 'certificateTemplate',
        'certificate_profile': 'certificateProfile',
        'certificate_auth_principal': 'certificateAuthPrincipal',
        'certificate_revoked_at': 'certificateRevokedAt',
        'certificate_revocation_reason': 'certificateRevocationReason',
        'certificate_storage_path': 'certificateStoragePath',
        'certificate_private_key_path': 'certificatePrivateKeyPath',
        'acme_order_id': 'acmeOrderID',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_certificate_record"
        verbose_name = "Certificate Record"
        verbose_name_plural = "Certificate Records"

    def __str__(self) -> str:
        return f"{self.cn} ({self.certificate_serial_number})"

    @property
    def dn(self) -> str:
        """Get the DN for this certificate record."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CERTIFICATES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class CertificateAuthority(LDAPModel):
    """Netcrave Certificate Authority.

    Based on netcrave-certificate.schema certificateAuthority object class.
    STRUCTURAL object class.

    MUST: cn
    MAY: description, certificateNotAfter

    Note: Schema appears truncated - implementation based on visible attributes.
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="caName",
        help_text="CA name (cn)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this Certificate Authority",
    )
    certificate_not_after = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="certificateNotAfter",
        help_text="CA certificate expiration time",
    )

    ldap_base_dn = settings.LDAP_OU_CERTIFICATES + "," + settings.LDAP_BASE_DN
    object_classes = ["certificateAuthority"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'description': 'description',
        'certificate_not_after': 'certificateNotAfter',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_certificate_authority"
        verbose_name = "Certificate Authority"
        verbose_name_plural = "Certificate Authorities"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this certificate authority."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CERTIFICATES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
