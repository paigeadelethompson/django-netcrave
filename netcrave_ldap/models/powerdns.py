"""
LDAP models for PowerDNS schema.

This module provides:
- PDNSDomain: DNS zone with template support
- PDNSRecord: DNS record with RRSet support
"""

import re
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import LDAPModel


class PDNSDomain(LDAPModel):
    """DNS zone domain model.

    Based on dnsdomain2.schema dNSDomain2 and pdns-domaininfo schema.
    STRUCTURAL object class.

    MUST: dc (domainComponent - zone name)
    MAY from dNSDomain2:
        dNSTTL, dNSClass, aRecord, aAAARecord, mxRecord, etc.
    """

    # Zone name (dc = domainComponent)
    dc = models.CharField(
        max_length=253,
        unique=True,
        verbose_name="domainName",
        help_text="DNS zone name (e.g., 'example.com')",
    )
    dnsttl = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=settings.LDAP_DEFAULT_DNS_TTL,
        verbose_name="dNSTTL",
        help_text="Default TTL for records in this zone",
    )
    dnsclass = models.CharField(
        max_length=10,
        default="IN",
        verbose_name="dNSClass",
        help_text="DNS class (usually 'IN' for Internet)",
    )
    pdns_domain_type = models.CharField(
        max_length=20,
        default="master",
        verbose_name="pdnsDomainType",
        help_text="Zone type: master, slave, secondary",
    )
    master_ips = models.JSONField(
        blank=True,
        default=list,
        verbose_name="masterIPs",
        help_text="List of master IP addresses for slave zones",
    )
    soa_record = models.JSONField(
        blank=True,
        null=True,
        verbose_name="soaRecord",
        help_text="SOA record configuration (dict with mname, rname, etc.)",
    )
    ns_records = models.JSONField(
        blank=True,
        default=list,
        verbose_name="nsRecords",
        help_text="List of NS record values (nameserver FQDNs)",
    )

    # SOA defaults
    soa_serial = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        help_text="Zone serial number (auto-generated if not set)",
    )
    soa_refresh = models.PositiveIntegerField(
        default=settings.LDAP_DEFAULT_SOA_REFRESH,
        verbose_name="SOA Refresh",
        help_text="Seconds between AXFR checks",
    )
    soa_retry = models.PositiveIntegerField(
        default=settings.LDAP_DEFAULT_SOA_RETRY,
        verbose_name="SOA Retry",
        help_text="Seconds after failed refresh before retrying",
    )
    soa_expiry = models.PositiveIntegerField(
        default=settings.LDAP_DEFAULT_SOA_EXPIRY,
        verbose_name="SOA Expiry",
        help_text="Seconds before zone is considered stale",
    )
    soa_minimum = models.PositiveIntegerField(
        default=settings.LDAP_DEFAULT_SOA_MIN_TTL,
        verbose_name="SOA Minimum TTL",
        help_text="Minimum TTL for negative responses",
    )

    ldap_base_dn = settings.LDAP_OU_DNS + "," + settings.LDAP_BASE_DN
    object_classes = ["dNSDomain2"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_pdns_domains"
        verbose_name = "DNS Zone (PDNS Domain)"
        verbose_name_plural = "DNS Zones"

    def __str__(self) -> str:
        return self.dc

    @property
    def dn(self) -> str:
        """Get the DN for this domain.

        DC values with dots are split into separate dc= components.
        E.g., 'example.com' -> 'dc=example,dc=com'
        """
        # Split domain name and create dc= parts
        parts = self.dc.split(".")
        dc_parts = ",".join(f"dc={part}" for part in parts)
        return f"{dc_parts},{settings.LDAP_OU_DNS},{settings.LDAP_BASE_DN}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def clean(self) -> None:
        """Validate the domain."""
        super().clean()
        self._validate_zone_name()

    def _validate_zone_name(self) -> None:
        """Validate zone name format."""
        # Basic DNS name validation
        if not re.match(r"^[a-zA-Z0-9.-]+$", self.dc):
            raise ValidationError(
                {"dc": "Zone name must contain only letters, numbers, dots, and hyphens"}
            )

        # Length check (253 chars max)
        if len(self.dc) > 253:
            raise ValidationError({"dc": "Zone name must be 253 characters or fewer"})

    def save(self, *args, **kwargs):
        """Generate SOA serial on save if not set."""
        from datetime import date

        if self.soa_serial is None:
            # Date-based serial: YYYYMMDD01
            today = date.today()
            self.soa_serial = int(today.strftime("%Y%m%d") + "01")

        super().save(*args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert domain to dictionary for serialization."""
        return {
            "dc": self.dc,
            "dn": self.dn,
            "dNSTTL": self.dnsttl or settings.LDAP_DEFAULT_DNS_TTL,
            "dNSClass": self.dnsclass,
            "pdnsDomainType": self.pdns_domain_type,
            "masterIPs": self.master_ips,
            "soaRecord": {
                "mname": self.soa_record.get("mname", "ns1." + self.dc)
                if self.soa_record
                else f"ns1.{self.dc}",
                "rname": self.soa_record.get("rname", "admin." + self.dc)
                if self.soa_record
                else f"admin.{self.dc}",
                "serial": self.soa_serial,
                "refresh": self.soa_refresh,
                "retry": self.soa_retry,
                "expiry": self.soa_expiry,
                "minimum": self.soa_minimum,
            } if (self.soa_record or True) else {
                "mname": f"ns1.{self.dc}",
                "rname": f"admin.{self.dc}",
                "serial": self.soa_serial,
                "refresh": self.soa_refresh,
                "retry": self.soa_retry,
                "expiry": self.soa_expiry,
                "minimum": self.soa_minimum,
            },
            "nsRecords": self.ns_records,
        }


class PDNSRecord(LDAPModel):
    """DNS record model.

    Based on dnsdomain2.schema dNSDomain2 and PdnsRecordData.
    Supports multiple record types with type-specific validation.

    Record Types:
    - A: IPv4 address
    - AAAA: IPv6 address
    - CNAME: Canonical name (alias)
    - MX: Mail exchange
    - NS: Name server
    - PTR: Pointer (reverse lookup)
    - TXT: Text record
    - SPF: Sender Policy Framework
    - SOA: Start of Authority
    - SRV: Service location
    - CAA: Certification Authority Authorization
    - DNSKEY, DS, NSEC, RRSIG, NSEC3: DNSSEC records
    - SSHFP: SSH fingerprint
    - TLSA: TLS authentication
    - CERT: Certificate record
    """

    # Record name (relative to zone or FQDN)
    dc = models.CharField(
        max_length=255,
        verbose_name="recordName",
        help_text="Record name (hostname relative to zone, or FQDN)",
    )
    dnsttl = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="dNSTTL",
        help_text="TTL for this record (optional, inherits from zone if not set)",
    )

    # Type-specific fields stored as JSON for flexibility
    record_type = models.CharField(
        max_length=10,
        choices=[
            ("A", "A (IPv4)"),
            ("AAAA", "AAAA (IPv6)"),
            ("CNAME", "CNAME (Alias)"),
            ("MX", "MX (Mail Exchange)"),
            ("NS", "NS (Name Server)"),
            ("PTR", "PTR (Pointer)"),
            ("TXT", "TXT (Text)"),
            ("SPF", "SPF (Sender Policy Framework)"),
            ("SOA", "SOA (Start of Authority)"),
            ("SRV", "SRV (Service Location)"),
            ("CAA", "CAA (Certificate Authority Authorization)"),
            ("DNSKEY", "DNSKEY (DNS Public Key)"),
            ("DS", "DS (Delegation Signer)"),
            ("NSEC", "NSEC (Next Secure)"),
            ("RRSIG", "RRSIG (Resource Record Signature)"),
            ("SSHFP", "SSHFP (SSH Fingerprint)"),
            ("TLSA", "TLSA (TLS Authentication)"),
            ("CERT", "CERT (Certificate)"),
        ],
        verbose_name="type",
        help_text="DNS record type",
    )

    # Value field - stores the main value based on record type
    value = models.TextField(
        blank=True,
        null=True,
        help_text="Record value (format varies by type)",
    )

    # Additional fields for complex records
    priority = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Priority/Weight (for MX, SRV)",
    )
    weight = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Weight (for SRV)",
    )
    port = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Port (for SRV, TLSA)",
    )

    # DNSSEC-specific fields
    flags = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="DNSKEY Flags",
        help_text="Flags field for DNSKEY/CAA records",
    )
    protocol = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Protocol field (for DNSKEY)",
    )
    algorithm = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Algorithm field (for DNSKEY, DS, SSHFP, TLSA)",
    )
    public_key = models.TextField(
        blank=True,
        null=True,
        verbose_name="Public Key/Data",
        help_text="Base64-encoded public key or data",
    )
    key_tag = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Key Tag",
        help_text="Key tag (for DS, CERT)",
    )
    digest_type = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Digest Type",
        help_text="Digest type (for DS, CAA)",
    )
    digest = models.TextField(
        blank=True,
        null=True,
        help_text="Digest value (for DS)",
    )
    signature = models.TextField(
        blank=True,
        null=True,
        help_text="Signature data (for RRSIG)",
    )
    type_covered = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Type Covered",
        help_text="Record type covered by signature (RRSIG)",
    )

    # Additional metadata
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about this record",
    )
    active = models.BooleanField(
        default=True,
        help_text="Whether this record is active/enabled",
    )

    ldap_base_dn = settings.LDAP_OU_DNS + "," + settings.LDAP_BASE_DN
    object_classes = ["dNSDomain2"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_pdns_records"
        verbose_name = "DNS Record"
        verbose_name_plural = "DNS Records"

    def __str__(self) -> str:
        return f"{self.dc} ({self.record_type})"

    @property
    def dn(self) -> str:
        """Get the DN for this record."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_DNS)
        # Use dc= prefix and convert dots to separate dc= components
        name_parts = self.dc.replace(".", ",dc=").split(",")
        if not name_parts[0].startswith("dc="):
            name_parts.insert(0, f"dc={self.dc.split('.')[0]}")
        return f"dc={''.join(name_parts)},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def clean(self) -> None:
        """Validate the record based on type."""
        super().clean()
        self._validate_record_type()

    def _validate_record_type(self) -> None:
        """Validate record value format based on type."""
        if not self.value:
            return  # Value may be optional for some types

        if self.record_type == "A":
            # IPv4 address validation
            parts = self.value.split(".")
            if len(parts) != 4:
                raise ValidationError(
                    {"value": "A record must contain exactly 4 octets"}
                )
            for part in parts:
                try:
                    val = int(part)
                    if val < 0 or val > 255:
                        raise ValidationError(
                            {"value": "Each A record octet must be 0-255"}
                        )
                except ValueError:
                    raise ValidationError(
                        {"value": "A record octets must be numeric"}
                    )

        elif self.record_type == "AAAA":
            # Basic IPv6 validation (not comprehensive)
            parts = self.value.split(":")
            if len(parts) < 3 or len(parts) > 8:
                raise ValidationError(
                    {"value": "Invalid IPv6 address format"}
                )

        elif self.record_type == "CNAME":
            # Must be a valid FQDN
            if not self.value.endswith(".") and "." in self.value:
                raise ValidationError(
                    {"value": "CNAME target should end with '.' (FQDN)"}
                )

        elif self.record_type == "MX":
            if self.priority is None or self.priority > 65535:
                raise ValidationError(
                    {"priority": "MX priority must be 0-65535"}
                )

        elif self.record_type == "TXT" and len(self.value) > 255:
            # RFC says each string in TXT should be <= 255 chars
            if len(self.value) > 255:
                raise ValidationError(
                    {"value": "TXT value must be 255 characters or fewer"}
                )

        elif self.record_type == "SRV":
            if None in [self.priority, self.weight, self.port]:
                raise ValidationError(
                    {
                        "priority": "SRV records require priority, weight, and port",
                        "weight": "SRV records require priority, weight, and port",
                        "port": "SRV records require priority, weight, and port",
                    }
                )

        elif self.record_type == "SOA":
            # SOA should be stored as JSON with mname, rname, serial, etc.
            try:
                import json

                soa_data = (
                    json.loads(self.value)
                    if isinstance(self.value, str)
                    else self.value
                )
                required = ["mname", "rname", "serial", "refresh", "retry", "expiry"]
                for field in required:
                    if field not in soa_data:
                        raise ValidationError(
                            {"value": f"SOA record missing required field: {field}"}
                        )
            except Exception as e:
                raise ValidationError({"value": f"Invalid SOA format: {str(e)}"})

    def get_value_display(self) -> str:
        """Get formatted value display based on record type."""
        if self.record_type == "MX":
            return f"{self.priority} {self.value}"
        elif self.record_type == "SRV":
            return f"{self.priority} {self.weight} {self.port} {self.value}"
        else:
            return self.value
