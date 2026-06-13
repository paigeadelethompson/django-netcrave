"""
LDAP models for COSINE schema (RFC1274).

This module provides:
- pilotObject: AUXILIARY object class with info, photo, manager, uniqueIdentifier
- pilotPerson: STRUCTURAL SUP person with userid, textEncodedORAddress, rfc822Mailbox, etc.
- account: STRUCTURAL MUST userid for computer accounts
- document: STRUCTURAL MUST documentIdentifier for documents
- room: STRUCTURAL MUST commonName for rooms
- domain: STRUCTURAL MUST domainComponent for DNS/NRS domains
- dNSDomain: STRUCTURAL SUP domain with DNS records (ARecord, MXRecord, etc.)
- domainRelatedObject: AUXILIARY MUST associatedDomain
- friendlyCountry: STRUCTURAL SUP country MUST friendlyCountryName
- simpleSecurityObject: AUXILIARY MUST userPassword
- pilotOrganization: STRUCTURAL SUP organization, organizationalUnit
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class PilotObject(LDAPModel):
    """Pilot Object (AUXILIARY).

    Based on cosine.schema pilotObject.
    AUXILIARY object class.

    MAY: info, photo, manager, uniqueIdentifier
    """

    cn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="commonName",
        help_text="Common name (optional for auxiliary)",
    )
    info = models.TextField(
        blank=True,
        null=True,
        verbose_name="info",
        help_text="General information about this object",
    )
    photo = models.BinaryField(
        blank=True,
        null=True,
        verbose_name="photo",
        help_text="Photo/G3 fax of the object",
    )
    manager = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="manager",
        help_text="DN of the manager",
    )
    unique_identifier = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="uniqueIdentifier",
        help_text="Unique identifier for this object",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this pilot object",
    )

    ldap_base_dn = settings.LDAP_BASE_DN
    object_classes = ["pilotObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'info': 'info',
        'photo': 'photo',
        'manager': 'manager',
        'unique_identifier': 'uniqueIdentifier',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_pilot_object"
        verbose_name = "Pilot Object"
        verbose_name_plural = "Pilot Objects"

    def __str__(self) -> str:
        return self.cn or f"PilotObject({self.pk})"

    @property
    def dn(self) -> str:
        """Get the DN for this pilot object."""
        from ..utils.dn import build_dn

        return build_dn({"cn": self.cn}) if self.cn else LDAPModel.dn.fget(self)  # type: ignore

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class PilotPerson(LDAPModel):
    """Pilot Person (STRUCTURAL, SUP person).

    Based on cosine.schema pilotPerson.
    STRUCTURAL object class.

    MUST: commonName, surname (from person)
    MAY: userid, textEncodedORAddress, rfc822Mailbox, favouriteDrink,
         roomNumber, userClass, homeTelephoneNumber, homePostalAddress,
         secretary, personalTitle, preferredDeliveryMethod, businessCategory,
         janetMailbox, otherMailbox, mobileTelephoneNumber, pagerTelephoneNumber,
         organizationalStatus, mailPreferenceOption, personalSignature
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="commonName",
        help_text="Common name (from person)",
    )
    sn = models.CharField(
        max_length=255,
        verbose_name="surname",
        help_text="Surname / last name (required by person superclass)",
    )
    userid = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="userid",
        help_text="Computer system login name",
    )
    text_encoded_or_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="textEncodedORAddress",
        help_text="X.400 O/R address (deprecated)",
    )
    rfc822_mailbox = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="rfc822Mailbox",
        help_text="Electronic mailbox (RFC 822)",
    )
    favourite_drink = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="favouriteDrink",
        help_text="Favorite drink",
    )
    room_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="roomNumber",
        help_text="Room number",
    )
    user_class = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="userClass",
        help_text="Category of computer user",
    )
    home_telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="homeTelephoneNumber",
        help_text="Home telephone number",
    )
    home_postal_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="homePostalAddress",
        help_text="Home postal address",
    )
    secretary = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="secretary",
        help_text="DN of the secretary",
    )
    personal_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="personalTitle",
        help_text="Personal title (Ms, Dr, Prof, etc.)",
    )
    preferred_delivery_method = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="preferredDeliveryMethod",
        help_text="Preferred delivery method",
    )
    business_category = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="businessCategory",
        help_text="Business category",
    )
    janet_mailbox = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="janetMailbox",
        help_text="Janet mailbox (UK academic mail)",
    )
    other_mailbox = models.TextField(
        blank=True,
        null=True,
        verbose_name="otherMailbox",
        help_text="Other mailbox types",
    )
    mobile_telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="mobileTelephoneNumber",
        help_text="Mobile telephone number",
    )
    pager_telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="pagerTelephoneNumber",
        help_text="Pager telephone number",
    )
    organizational_status = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalStatus",
        help_text="Organizational status (student, researcher, etc.)",
    )
    mail_preference_option = models.IntegerField(
        blank=True,
        null=True,
        choices=[(0, "no-list-inclusion"), (1, "any-list-inclusion"), (2, "professional-list-inclusion")],
        verbose_name="mailPreferenceOption",
        help_text="Mail preference option",
    )
    personal_signature = models.BinaryField(
        blank=True,
        null=True,
        verbose_name="personalSignature",
        help_text="Personal signature (G3 fax)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this pilot person",
    )

    ldap_base_dn = getattr(settings, "LDAP_OU_PEOPLE", "ou=people") + "," + settings.LDAP_BASE_DN
    object_classes = ["pilotPerson"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'sn': 'sn',
        'userid': 'userid',
        'text_encoded_or_address': 'textEncodedORAddress',
        'rfc822_mailbox': 'rfc822Mailbox',
        'favourite_drink': 'favouriteDrink',
        'room_number': 'roomNumber',
        'user_class': 'userClass',
        'home_telephone_number': 'homeTelephoneNumber',
        'home_postal_address': 'homePostalAddress',
        'secretary': 'secretary',
        'personal_title': 'personalTitle',
        'preferred_delivery_method': 'preferredDeliveryMethod',
        'business_category': 'businessCategory',
        'janet_mailbox': 'janetMailbox',
        'other_mailbox': 'otherMailbox',
        'mobile_telephone_number': 'mobileTelephoneNumber',
        'pager_telephone_number': 'pagerTelephoneNumber',
        'organizational_status': 'organizationalStatus',
        'mail_preference_option': 'mailPreferenceOption',
        'personal_signature': 'personalSignature',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_pilot_person"
        verbose_name = "Pilot Person"
        verbose_name_plural = "Pilot Persons"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this pilot person."""
        from ..utils.dn import build_ou

        base = getattr(settings, "LDAP_OU_PEOPLE", "ou=people")
        return f"cn={self.cn},ou={base},{settings.LDAP_BASE_DN}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class Account(LDAPModel):
    """Account (STRUCTURAL).

    Based on cosine.schema account.
    STRUCTURAL object class.

    MUST: userid
    MAY: description, seeAlso, localityName, organizationName,
         organizationalUnitName, host
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="userid",
        help_text="User ID / computer system login name (used for naming)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this account",
    )
    see_also = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="seeAlso",
        help_text="DN of related entry",
    )
    locality_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="localityName",
        help_text="Locality name",
    )
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationName",
        help_text="Organization name",
    )
    organizational_unit_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalUnitName",
        help_text="Organizational unit name",
    )
    host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Host computer",
    )

    ldap_base_dn = getattr(settings, "LDAP_OU_ACCOUNTS", "ou=accounts") + "," + settings.LDAP_BASE_DN
    object_classes = ["account"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'userid',
        'description': 'description',
        'see_also': 'seeAlso',
        'locality_name': 'localityName',
        'organization_name': 'organizationName',
        'organizational_unit_name': 'organizationalUnitName',
        'host': 'host',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_account"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this account."""
        from ..utils.dn import build_ou

        base = getattr(settings, "LDAP_OU_ACCOUNTS", "ou=accounts")
        return f"cn={self.cn},ou={base},{settings.LDAP_BASE_DN}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class Document(LDAPModel):
    """Document (STRUCTURAL).

    Based on cosine.schema document.
    STRUCTURAL object class.

    MUST: documentIdentifier
    MAY: commonName, description, seeAlso, localityName,
         organizationName, organizationalUnitName, documentTitle,
         documentVersion, documentAuthor, documentLocation, documentPublisher
    """

    document_identifier = models.CharField(
        max_length=255,
        verbose_name="documentIdentifier",
        help_text="Unique identifier of document (used for naming)",
    )
    common_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="commonName",
        help_text="Common name/title",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this document",
    )
    see_also = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="seeAlso",
        help_text="DN of related entry",
    )
    locality_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="localityName",
        help_text="Locality name",
    )
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationName",
        help_text="Organization name",
    )
    organizational_unit_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalUnitName",
        help_text="Organizational unit name",
    )
    document_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="documentTitle",
        help_text="Title of document",
    )
    document_version = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="documentVersion",
        help_text="Version of document",
    )
    document_author = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="documentAuthor",
        help_text="DN of author of document",
    )
    document_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="documentLocation",
        help_text="Location of document original",
    )
    document_publisher = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="documentPublisher",
        help_text="Publisher of document",
    )

    ldap_base_dn = getattr(settings, "LDAP_OU_DOCUMENTS", "ou=documents") + "," + settings.LDAP_BASE_DN
    object_classes = ["document"]

    ldap_attributes_map: Dict[str, str] = {
        'document_identifier': 'documentIdentifier',
        'common_name': 'commonName',
        'description': 'description',
        'see_also': 'seeAlso',
        'locality_name': 'localityName',
        'organization_name': 'organizationName',
        'organizational_unit_name': 'organizationalUnitName',
        'document_title': 'documentTitle',
        'document_version': 'documentVersion',
        'document_author': 'documentAuthor',
        'document_location': 'documentLocation',
        'document_publisher': 'documentPublisher',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_document"
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self) -> str:
        return self.common_name or self.document_identifier

    @property
    def dn(self) -> str:
        """Get the DN for this document."""
        from ..utils.dn import build_ou

        base = getattr(settings, "LDAP_OU_DOCUMENTS", "ou=documents")
        return f"cn={self.common_name or self.document_identifier},ou={base},{settings.LDAP_BASE_DN}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class Room(LDAPModel):
    """Room (STRUCTURAL).

    Based on cosine.schema room.
    STRUCTURAL object class.

    MUST: commonName
    MAY: roomNumber, description, seeAlso, telephoneNumber
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="commonName",
        help_text="Room name/number (used for naming)",
    )
    room_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="roomNumber",
        help_text="Room number",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this room",
    )
    see_also = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="seeAlso",
        help_text="DN of related entry",
    )
    telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="telephoneNumber",
        help_text="Telephone number",
    )

    ldap_base_dn = getattr(settings, "LDAP_OU_ROOMS", "ou=rooms") + "," + settings.LDAP_BASE_DN
    object_classes = ["room"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'commonName',
        'room_number': 'roomNumber',
        'description': 'description',
        'see_also': 'seeAlso',
        'telephone_number': 'telephoneNumber',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_room"
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this room."""
        from ..utils.dn import build_ou

        base = getattr(settings, "LDAP_OU_ROOMS", "ou=rooms")
        return f"cn={self.cn},ou={base},{settings.LDAP_BASE_DN}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class Domain(LDAPModel):
    """Domain (STRUCTURAL).

    Based on cosine.schema domain.
    STRUCTURAL object class.

    MUST: domainComponent
    MAY: associatedName, organizationName, description,
         businessCategory, seeAlso, searchGuide, userPassword,
         localityName, stateOrProvinceName, streetAddress,
         physicalDeliveryOfficeName, postalAddress, postalCode,
         postOfficeBox, streetAddress, facsimileTelephoneNumber,
         internationalISDNNumber, telephoneNumber, teletexTerminalIdentifier,
         telexNumber, preferredDeliveryMethod, destinationIndicator,
         registeredAddress, x121Address
    """

    dc = models.CharField(
        max_length=255,
        verbose_name="domainComponent",
        help_text="DNS/NRS domain component (used for naming)",
    )
    associated_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="associatedName",
        help_text="DN of entry associated with domain",
    )
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationName",
        help_text="Organization name",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this domain",
    )
    business_category = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="businessCategory",
        help_text="Business category",
    )
    see_also = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="seeAlso",
        help_text="DN of related entry",
    )
    search_guide = models.TextField(
        blank=True,
        null=True,
        verbose_name="searchGuide",
        help_text="Search guide (deprecated)",
    )
    user_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="userPassword",
        help_text="User password (for simpleSecurityObject)",
    )

    ldap_base_dn = settings.LDAP_OU_DOMAINS + "," + settings.LDAP_BASE_DN
    object_classes = ["domain"]

    ldap_attributes_map: Dict[str, str] = {
        'dc': 'domainComponent',
        'associated_name': 'associatedName',
        'organization_name': 'organizationName',
        'description': 'description',
        'business_category': 'businessCategory',
        'see_also': 'seeAlso',
        'search_guide': 'searchGuide',
        'user_password': 'userPassword',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_domain"
        verbose_name = "Domain"
        verbose_name_plural = "Domains"

    def __str__(self) -> str:
        return self.dc

    @property
    def dn(self) -> str:
        """Get the DN for this domain."""
        from ..utils.dn import build_dn

        return build_dn({"dc": self.dc})

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class DNSDomain(LDAPModel):
    """DNS Domain (STRUCTURAL, SUP domain).

    Based on cosine.schema dNSDomain.
    STRUCTURAL object class.

    MUST: domainComponent (from domain)
    MAY: ARecord, MDRecord, MXRecord, NSRecord, SOARecord, CNAMERecord
    """

    dc = models.CharField(
        max_length=255,
        verbose_name="domainComponent",
        help_text="DNS/NRS domain component (used for naming)",
    )
    a_record = models.TextField(
        blank=True,
        null=True,
        verbose_name="ARecord",
        help_text="DNS A record",
    )
    md_record = models.TextField(
        blank=True,
        null=True,
        verbose_name="MDRecord",
        help_text="DNS MD record (deprecated)",
    )
    mx_record = models.TextField(
        blank=True,
        null=True,
        verbose_name="MXRecord",
        help_text="DNS MX record (mail exchange)",
    )
    ns_record = models.TextField(
        blank=True,
        null=True,
        verbose_name="NSRecord",
        help_text="DNS NS record (name server)",
    )
    soa_record = models.TextField(
        blank=True,
        null=True,
        verbose_name="SOARecord",
        help_text="DNS SOA record (start of authority)",
    )
    cname_record = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="CNAMERecord",
        help_text="DNS CNAME record (canonical name)",
    )

    ldap_base_dn = settings.LDAP_OU_DNS + "," + settings.LDAP_BASE_DN
    object_classes = ["dNSDomain"]

    ldap_attributes_map: Dict[str, str] = {
        'dc': 'domainComponent',
        'a_record': 'aRecord',
        'md_record': 'mDRecord',
        'mx_record': 'mXRecord',
        'ns_record': 'nSRecord',
        'soa_record': 'sOARecord',
        'cname_record': 'cNAMERecord',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_dns_domain"
        verbose_name = "DNS Domain"
        verbose_name_plural = "DNS Domains"

    def __str__(self) -> str:
        return self.dc

    @property
    def dn(self) -> str:
        """Get the DN for this DNS domain."""
        from ..utils.dn import build_dn

        return build_dn({"dc": self.dc})

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class DomainRelatedObject(LDAPModel):
    """Domain Related Object (AUXILIARY).

    Based on cosine.schema domainRelatedObject.
    AUXILIARY object class.

    MUST: associatedDomain
    """

    cn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="commonName",
        help_text="Common name (optional for auxiliary)",
    )
    associated_domain = models.CharField(
        max_length=255,
        verbose_name="associatedDomain",
        help_text="Associated DNS/NRS domain",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this domain related object",
    )

    ldap_base_dn = settings.LDAP_BASE_DN
    object_classes = ["domainRelatedObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'associated_domain': 'associatedDomain',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_domain_related"
        verbose_name = "Domain Related Object"
        verbose_name_plural = "Domain Related Objects"

    def __str__(self) -> str:
        return self.associated_domain

    @property
    def dn(self) -> str:
        """Get the DN for this domain related object."""
        from ..utils.dn import build_dn

        return build_dn({"cn": self.cn}) if self.cn else LDAPModel.dn.fget(self)  # type: ignore

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class FriendlyCountry(LDAPModel):
    """Friendly Country (STRUCTURAL, SUP country).

    Based on cosine.schema friendlyCountry.
    STRUCTURAL object class.

    MUST: friendlyCountryName
    MAY: description, searchGuide (from country)
    """

    co = models.CharField(
        max_length=255,
        verbose_name="friendlyCountryName",
        help_text="Friendly country name (used for naming)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this country",
    )
    search_guide = models.TextField(
        blank=True,
        null=True,
        verbose_name="searchGuide",
        help_text="Search guide (deprecated)",
    )

    ldap_base_dn = settings.LDAP_OU_COUNTRIES + "," + settings.LDAP_BASE_DN
    object_classes = ["friendlyCountry"]

    ldap_attributes_map: Dict[str, str] = {
        'co': 'friendlyCountryName',
        'description': 'description',
        'search_guide': 'searchGuide',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_friendly_country"
        verbose_name = "Friendly Country"
        verbose_name_plural = "Friendly Countries"

    def __str__(self) -> str:
        return self.co

    @property
    def dn(self) -> str:
        """Get the DN for this friendly country."""
        from ..utils.dn import build_dn

        return build_dn({"co": self.co})

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class SimpleSecurityObject(LDAPModel):
    """Simple Security Object (AUXILIARY).

    Based on cosine.schema simpleSecurityObject.
    AUXILIARY object class.

    MUST: userPassword
    """

    cn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="commonName",
        help_text="Common name (optional for auxiliary)",
    )
    user_password = models.CharField(
        max_length=255,
        verbose_name="userPassword",
        help_text="User password (required)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this security object",
    )

    ldap_base_dn = settings.LDAP_BASE_DN
    object_classes = ["simpleSecurityObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'user_password': 'userPassword',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_security_object"
        verbose_name = "Simple Security Object"
        verbose_name_plural = "Simple Security Objects"

    def __str__(self) -> str:
        return self.cn or "SecurityObject"

    @property
    def dn(self) -> str:
        """Get the DN for this security object."""
        from ..utils.dn import build_dn

        return build_dn({"cn": self.cn}) if self.cn else LDAPModel.dn.fget(self)  # type: ignore

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class PilotOrganization(LDAPModel):
    """Pilot Organization (STRUCTURAL, SUP organization, organizationalUnit).

    Based on cosine.schema pilotOrganization.
    STRUCTURAL object class.

    MUST: organizationName OR organizationalUnitName
    MAY: buildingName
    """

    cn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="commonName",
        help_text="Common name (for organizationalRole fallback)",
    )
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationName",
        help_text="Organization name",
    )
    organizational_unit_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalUnitName",
        help_text="Organizational unit name",
    )
    building_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="buildingName",
        help_text="Name of the building",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this pilot organization",
    )

    ldap_base_dn = settings.LDAP_OU_ORGANIZATIONS + "," + settings.LDAP_BASE_DN
    object_classes = ["pilotOrganization"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'commonName',
        'organization_name': 'organizationName',
        'organizational_unit_name': 'organizationalUnitName',
        'building_name': 'buildingName',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_pilot_organization"
        verbose_name = "Pilot Organization"
        verbose_name_plural = "Pilot Organizations"

    def __str__(self) -> str:
        return self.organization_name or self.organizational_unit_name or self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this pilot organization."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_ORGANIZATIONS)
        if self.organization_name:
            return f"o={self.organization_name},{base}"
        elif self.organizational_unit_name:
            return f"ou={self.organizational_unit_name},{base}"
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
