"""
LDAP models for OpenLDAP Core schemas.

This module provides:
- person: Basic person object
- organizationalPerson: Person with organization attributes
- organizationalRole: Role within an organization
- residentialPerson: Person with residence info
- applicationProcess: Application process entry
- device: Generic device
- certificationAuthority: CA certificate holder
- pkiUser: PKI user
- dcObject: Domain component object
- uidObject: UID object (RFC2377)
- labeledURIObject: URI object with label
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class Person(LDAPModel):
    """Person model.

    Based on person from core.schema.
    STRUCTURAL object class.

    MUST: cn, sn (surname)
    MAY: userPassword, telephoneNumber, seeAlso, description
    """

    cn = models.CharField(
        max_length=255,
        help_text="Common name",
    )
    sn = models.CharField(
        max_length=255,
        verbose_name="surname",
        help_text="Surname (last name)",
    )
    user_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="userPassword",
        help_text="User password hash",
    )
    telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="telephoneNumber",
        help_text="Telephone number",
    )
    see_also = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="seeAlso",
        help_text="DN of related object",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this person",
    )

    ldap_base_dn = settings.LDAP_OU_PEOPLE + "," + settings.LDAP_BASE_DN
    object_classes = ["person"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'sn': 'sn',
        'user_password': 'userPassword',
        'telephone_number': 'telephoneNumber',
        'see_also': 'seeAlso',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_persons"
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this person."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_PEOPLE)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class OrganizationalPerson(LDAPModel):
    """Organizational person model.

    Based on organizationalPerson from core.schema.
    STRUCTURAL object class (extends person).

    MAY: title, x121Address, registeredAddress, destinationIndicator,
         preferredDeliveryMethod, telexNumber, teletexTerminalIdentifier,
         telephoneNumber, internationalISDNNumber, facsimileTelephoneNumber,
         street, postOfficeBox, postalCode, postalAddress,
         physicalDeliveryOfficeName, ou, st, l
    """

    cn = models.CharField(
        max_length=255,
        help_text="Common name",
    )
    sn = models.CharField(
        max_length=255,
        verbose_name="surname",
        help_text="Surname (last name)",
    )

    # Organization attributes
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Job title",
    )
    ou = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalUnit",
        help_text="Organizational unit",
    )

    # Address attributes
    street = models.TextField(
        blank=True,
        null=True,
        help_text="Street address",
    )
    post_office_box = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="postOfficeBox",
        help_text="Post office box",
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="postalCode",
        help_text="Postal code",
    )
    postal_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="postalAddress",
        help_text="Postal address",
    )

    # Location attributes
    l = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="localityName",
        help_text="Locality name (city)",
    )
    st = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="stateOrProvinceName",
        help_text="State or province name",
    )

    # Contact attributes
    telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="telephoneNumber",
        help_text="Telephone number",
    )
    international_isdn_number = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name="internationalISDNNumber",
        help_text="International ISDN number",
    )
    facsimile_telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="facsimileTelephoneNumber",
        help_text="Fax number",
    )

    # Physical attributes
    physical_delivery_office_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="physicalDeliveryOfficeName",
        help_text="Physical delivery office name",
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this person",
    )

    ldap_base_dn = settings.LDAP_OU_PEOPLE + "," + settings.LDAP_BASE_DN
    object_classes = ["organizationalPerson"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'sn': 'sn',
        'title': 'title',
        'ou': 'ou',
        'street': 'street',
        'post_office_box': 'postOfficeBox',
        'postal_code': 'postalCode',
        'postal_address': 'postalAddress',
        'l': 'l',
        'st': 'st',
        'telephone_number': 'telephoneNumber',
        'international_isdn_number': 'internationalISDNNumber',
        'facsimile_telephone_number': 'facsimileTelephoneNumber',
        'physical_delivery_office_name': 'physicalDeliveryOfficeName',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_organizational_persons"
        verbose_name = "Organizational Person"
        verbose_name_plural = "Organizational People"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this person."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_PEOPLE)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class OrganizationalRole(LDAPModel):
    """Organizational role model.

    Based on organizationalRole from core.schema.
    STRUCTURAL object class.

    MUST: cn
    MAY: x121Address, registeredAddress, destinationIndicator,
         preferredDeliveryMethod, telexNumber, teletexTerminalIdentifier,
         telephoneNumber, internationalISDNNumber, facsimileTelephoneNumber,
         seeAlso, roleOccupant, preferredDeliveryMethod, street,
         postOfficeBox, postalCode, postalAddress,
         physicalDeliveryOfficeName, ou, st, l, description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="roleName",
        help_text="Role name (cn)",
    )
    role_occupant = models.JSONField(
        blank=True,
        default=list,
        verbose_name="roleOccupant",
        help_text="List of DNs of people occupying this role",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this role",
    )

    ldap_base_dn = settings.LDAP_OU_ROLES + "," + settings.LDAP_BASE_DN
    object_classes = ["organizationalRole"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'role_occupant': 'roleOccupant',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_organizational_roles"
        verbose_name = "Organizational Role"
        verbose_name_plural = "Organizational Roles"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this role."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_ROLES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class ResidentialPerson(LDAPModel):
    """Residential person model.

    Based on residentialPerson from core.schema.
    STRUCTURAL object class (extends person).

    MUST: l (locality)
    MAY: businessCategory, x121Address, registeredAddress,
         destinationIndicator, preferredDeliveryMethod, telexNumber,
         teletexTerminalIdentifier, telephoneNumber, internationalISDNNumber,
         facsimileTelephoneNumber, street, postOfficeBox, postalCode,
         postalAddress, physicalDeliveryOfficeName, st, l
    """

    cn = models.CharField(
        max_length=255,
        help_text="Common name",
    )
    sn = models.CharField(
        max_length=255,
        verbose_name="surname",
        help_text="Surname (last name)",
    )
    l = models.CharField(
        max_length=255,
        verbose_name="localityName",
        help_text="Locality (required - city where person resides)",
    )

    # Address attributes
    street = models.TextField(
        blank=True,
        null=True,
        help_text="Street address",
    )
    post_office_box = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="postOfficeBox",
        help_text="Post office box",
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="postalCode",
        help_text="Postal code",
    )
    postal_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="postalAddress",
        help_text="Postal address",
    )

    # Contact attributes
    telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="telephoneNumber",
        help_text="Telephone number",
    )
    facsimile_telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="facsimileTelephoneNumber",
        help_text="Fax number",
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this person",
    )

    ldap_base_dn = settings.LDAP_OU_PEOPLE + "," + settings.LDAP_BASE_DN
    object_classes = ["residentialPerson"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'sn': 'sn',
        'l': 'l',
        'street': 'street',
        'post_office_box': 'postOfficeBox',
        'postal_code': 'postalCode',
        'postal_address': 'postalAddress',
        'telephone_number': 'telephoneNumber',
        'facsimile_telephone_number': 'facsimileTelephoneNumber',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_residential_persons"
        verbose_name = "Residential Person"
        verbose_name_plural = "Residential People"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this person."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_PEOPLE)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class ApplicationProcess(LDAPModel):
    """Application process model.

    Based on applicationProcess from core.schema.
    STRUCTURAL object class.

    MUST: cn
    MAY: seeAlso, ou, l, description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="processName",
        help_text="Process name (cn)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this process",
    )

    ldap_base_dn = settings.LDAP_OU_APPLICATIONS + "," + settings.LDAP_BASE_DN
    object_classes = ["applicationProcess"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_application_processes"
        verbose_name = "Application Process"
        verbose_name_plural = "Application Processes"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this process."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_APPLICATIONS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class Device(LDAPModel):
    """Device model.

    Based on device from core.schema.
    STRUCTURAL object class.

    MUST: cn
    MAY: serialNumber, seeAlso, owner, ou, o, l, description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="deviceName",
        help_text="Device name (cn)",
    )
    serial_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="serialNumber",
        help_text="Serial number of the device",
    )
    owner = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Owner DN",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this device",
    )

    ldap_base_dn = settings.LDAP_OU_DEVICES + "," + settings.LDAP_BASE_DN
    object_classes = ["device"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'serial_number': 'serialNumber',
        'owner': 'owner',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_devices"
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this device."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_DEVICES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class CertificationAuthority(LDAPModel):
    """Certification Authority model.

    Based on certificationAuthority from core.schema.
    AUXILIARY object class.

    MUST: authorityRevocationList, certificateRevocationList, cACertificate
    MAY: crossCertificatePair
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="caName",
        help_text="CA name (cn)",
    )

    # Certificate attributes (stored as references/paths in practice)
    authority_revocation_list = models.TextField(
        blank=True,
        null=True,
        verbose_name="authorityRevocationList",
        help_text="Path or reference to ARL",
    )
    certificate_revocation_list = models.TextField(
        blank=True,
        null=True,
        verbose_name="certificateRevocationList",
        help_text="Path or reference to CRL",
    )
    ca_certificate = models.TextField(
        blank=True,
        null=True,
        verbose_name="cACertificate",
        help_text="CA certificate (PEM format or path)",
    )
    cross_certificate_pair = models.TextField(
        blank=True,
        null=True,
        verbose_name="crossCertificatePair",
        help_text="Cross certificate pair",
    )

    ldap_base_dn = settings.LDAP_OU_CA + "," + settings.LDAP_BASE_DN
    object_classes = ["certificationAuthority"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'authority_revocation_list': 'authorityRevocationList',
        'certificate_revocation_list': 'certificateRevocationList',
        'ca_certificate': 'cACertificate',
        'cross_certificate_pair': 'crossCertificatePair',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_certification_authorities"
        verbose_name = "Certification Authority"
        verbose_name_plural = "Certification Authorities"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this CA."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class PkiUser(LDAPModel):
    """PKI User model.

    Based on pkiUser from core.schema.
    AUXILIARY object class.

    MAY: userCertificate
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="userName",
        help_text="User name (cn)",
    )
    user_certificate = models.TextField(
        blank=True,
        null=True,
        verbose_name="userCertificate",
        help_text="User certificate (PEM format or path)",
    )

    ldap_base_dn = settings.LDAP_OU_USERS + "," + settings.LDAP_BASE_DN
    object_classes = ["pkiUser"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'user_certificate': 'userCertificate',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_pki_users"
        verbose_name = "PKI User"
        verbose_name_plural = "PKI Users"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this user."""
        from ..utils.dn import build_user_dn

        return build_user_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class DcObject(LDAPModel):
    """Domain component object model.

    Based on dcObject from RFC 2247.
    AUXILIARY object class.

    MUST: dc (domainComponent)
    """

    dc = models.CharField(
        max_length=253,
        unique=True,
        verbose_name="domainComponent",
        help_text="Domain component (e.g., 'example' for example.com)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this domain component",
    )

    ldap_base_dn = settings.LDAP_BASE_DN
    object_classes = ["dcObject"]

    ldap_attributes_map: Dict[str, str] = {
        'dc': 'dc',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_dc_objects"
        verbose_name = "Domain Component Object"
        verbose_name_plural = "Domain Component Objects"

    def __str__(self) -> str:
        return self.dc

    @property
    def dn(self) -> str:
        """Get the DN for this domain component."""
        return f"dc={self.dc},{settings.LDAP_BASE_DN}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class UidObject(LDAPModel):
    """UID object model (RFC 2377).

    Based on uidObject from RFC 2377.
    AUXILIARY object class.

    MUST: uid
    """

    uid = models.CharField(
        max_length=255,
        unique=True,
        help_text="User ID",
    )

    ldap_base_dn = settings.LDAP_OU_USERS + "," + settings.LDAP_BASE_DN
    object_classes = ["uidObject"]

    ldap_attributes_map: Dict[str, str] = {
        'uid': 'uid',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_uid_objects"
        verbose_name = "UID Object"
        verbose_name_plural = "UID Objects"

    def __str__(self) -> str:
        return self.uid

    @property
    def dn(self) -> str:
        """Get the DN for this UID object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_USERS)
        return f"uid={self.uid},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class LabeledURIObject(LDAPModel):
    """Labeled URI object model (RFC 2079).

    Based on labeledURIObject from RFC 2079.
    AUXILIARY object class.

    MAY: labeledURI
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="uriName",
        help_text="URI name (cn)",
    )
    labeled_uri = models.TextField(
        blank=True,
        null=True,
        verbose_name="labeledURI",
        help_text="Uniform Resource Identifier with optional label",
    )

    ldap_base_dn = settings.LDAP_OU_RESOURCES + "," + settings.LDAP_BASE_DN
    object_classes = ["labeledURIObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'labeled_uri': 'labeledURI',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_labeled_uri_objects"
        verbose_name = "Labeled URI Object"
        verbose_name_plural = "Labeled URI Objects"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_RESOURCES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class DSA(LDAPModel):
    """Directory System Agent (DSA).

    Based on dSA from core.schema.
    STRUCTURAL object class (extends applicationEntity).

    MAY: knowledgeInformation
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="dsaName",
        help_text="DSA name (cn)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this DSA",
    )

    ldap_base_dn = settings.LDAP_OU_DSAS + "," + settings.LDAP_BASE_DN
    object_classes = ["dSA"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_dsas"
        verbose_name = "DSA"
        verbose_name_plural = "DSAs"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this DSA."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_DSAS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class StrongAuthenticationUser(LDAPModel):
    """Strong authentication user.

    Based on strongAuthenticationUser from core.schema.
    AUXILIARY object class.

    MUST: userCertificate
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="userName",
        help_text="User name (cn)",
    )
    user_certificate = models.TextField(
        verbose_name="userCertificate",
        help_text="User certificate (PEM format or path)",
    )

    ldap_base_dn = settings.LDAP_OU_USERS + "," + settings.LDAP_BASE_DN
    object_classes = ["strongAuthenticationUser"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'user_certificate': 'userCertificate',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_strong_auth_users"
        verbose_name = "Strong Authentication User"
        verbose_name_plural = "Strong Authentication Users"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this user."""
        from ..utils.dn import build_user_dn

        return build_user_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class CRLDistributionPoint(LDAPModel):
    """Certificate Revocation List Distribution Point.

    Based on cRLDistributionPoint from core.schema.
    STRUCTURAL object class.

    MUST: cn, certificateRevocationList, authorityRevocationList
    MAY: cACertificate, crossCertificatePair
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="crlName",
        help_text="CRL name (cn)",
    )
    certificate_revocation_list = models.TextField(
        verbose_name="certificateRevocationList",
        help_text="Path or reference to CRL",
    )
    authority_revocation_list = models.TextField(
        verbose_name="authorityRevocationList",
        help_text="Path or reference to ARL",
    )
    ca_certificate = models.TextField(
        blank=True,
        null=True,
        verbose_name="cACertificate",
        help_text="CA certificate (PEM format or path)",
    )
    cross_certificate_pair = models.TextField(
        blank=True,
        null=True,
        verbose_name="crossCertificatePair",
        help_text="Cross certificate pair",
    )

    ldap_base_dn = settings.LDAP_OU_CA + "," + settings.LDAP_BASE_DN
    object_classes = ["cRLDistributionPoint"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'certificate_revocation_list': 'certificateRevocationList',
        'authority_revocation_list': 'authorityRevocationList',
        'ca_certificate': 'cACertificate',
        'cross_certificate_pair': 'crossCertificatePair',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_crl_distribution_points"
        verbose_name = "CRL Distribution Point"
        verbose_name_plural = "CRL Distribution Points"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this CRL distribution point."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class DeltaCRL(LDAPModel):
    """Delta Certificate Revocation List.

    Based on deltaCRL from core.schema.
    STRUCTURAL object class.

    MUST: cn, baseCertificateList
    MAY: certificateRevocationList, authorityRevocationList,
         cACertificate, crossCertificatePair
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="deltaCRLName",
        help_text="Delta CRL name (cn)",
    )
    base_certificate_list = models.TextField(
        verbose_name="baseCertificateList",
        help_text="Base certificate list reference",
    )
    certificate_revocation_list = models.TextField(
        blank=True,
        null=True,
        verbose_name="certificateRevocationList",
        help_text="Full CRL reference",
    )
    authority_revocation_list = models.TextField(
        blank=True,
        null=True,
        verbose_name="authorityRevocationList",
        help_text="ARL reference",
    )

    ldap_base_dn = settings.LDAP_OU_CA + "," + settings.LDAP_BASE_DN
    object_classes = ["deltaCRL"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'base_certificate_list': 'baseCertificateList',
        'certificate_revocation_list': 'certificateRevocationList',
        'authority_revocation_list': 'authorityRevocationList',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_delta_crl"
        verbose_name = "Delta CRL"
        verbose_name_plural = "Delta CRLs"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this delta CRL."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class DMD(LDAPModel):
    """Directory Management Domain.

    Based on dmd from core.schema.
    STRUCTURAL object class.

    MUST: cn, domainComponent
    MAY: userPassword, searchGuide, seeAlso,
         businessCategory, jurisdictionCountryName,
         legalOriginName, legalPersonalityName,
         LOCALITY_NAME, stateOrProvinceName, postOfficeBox,
         postalCode, streetAddress, physicalDeliveryOfficeName,
         postalAddress, registeredAddress, destinationIndicator,
         preferredDeliveryMethod, telexNumber, teletexTerminalIdentifier,
         telephoneNumber, internationalISDNNumber, facsimileTelephoneNumber,
         x121Address, internetDomainSuffix
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="dmdName",
        help_text="DMD name (cn)",
    )
    dc = models.CharField(
        max_length=253,
        unique=True,
        verbose_name="domainComponent",
        help_text="Domain component",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this DMD",
    )

    ldap_base_dn = settings.LDAP_BASE_DN
    object_classes = ["dmd"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'dc': 'dc',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_dmd"
        verbose_name = "Directory Management Domain"
        verbose_name_plural = "Directory Management Domains"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this DMD."""
        return f"cn={self.cn},{settings.LDAP_BASE_DN}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class PKICA(LDAPModel):
    """PKI Certificate Authority.

    Based on pkiCA from core.schema.
    STRUCTURAL object class.

    MUST: cn, cACertificate
    MAY: certificateRevocationList, authorityRevocationList,
         crossCertificatePair, dSAQuality
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="caName",
        help_text="CA name (cn)",
    )
    ca_certificate = models.TextField(
        verbose_name="cACertificate",
        help_text="CA certificate (PEM format or path)",
    )
    certificate_revocation_list = models.TextField(
        blank=True,
        null=True,
        verbose_name="certificateRevocationList",
        help_text="Path or reference to CRL",
    )
    authority_revocation_list = models.TextField(
        blank=True,
        null=True,
        verbose_name="authorityRevocationList",
        help_text="Path or reference to ARL",
    )
    cross_certificate_pair = models.TextField(
        blank=True,
        null=True,
        verbose_name="crossCertificatePair",
        help_text="Cross certificate pair",
    )

    ldap_base_dn = settings.LDAP_OU_CA + "," + settings.LDAP_BASE_DN
    object_classes = ["pkiCA"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'ca_certificate': 'cACertificate',
        'certificate_revocation_list': 'certificateRevocationList',
        'authority_revocation_list': 'authorityRevocationList',
        'cross_certificate_pair': 'crossCertificatePair',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_pki_ca"
        verbose_name = "PKI Certificate Authority"
        verbose_name_plural = "PKI Certificate Authorities"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this PKI CA."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_CA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

