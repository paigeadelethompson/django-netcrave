"""
LDAP Models for Django-LDAP integration.
This package provides LDAP-backed Django models for managing:
- Users (inetOrgPerson + posixAccount + kerberos + radius)
- Groups (posixGroup, groupOfNames, groupOfUniqueNames)
- Shadow accounts (shadowAccount)
- NIS objects (nisObject, ipService, ipNetwork, nisNetgroup, etc.)
- Computers (device + ipHost)
- PowerDNS (dNSDomain2 + PdnsDomain/PdnsRecord)
- Asterisk (extensions, IAX/SIP endpoints, voicemail)
- Radius (radiusprofile aux, radiusClient)
- Kerberos (krbRealmContainer, krbPrincipal, policies)
- Sendmail (MTA servers, maps/aliases)
- Postfix (alias, transport maps)
- OpenDKIM (email signing selectors and keys)
- LDAPNS (GSS-API authorized services, host objects, login status)
- Netcrave ICAP (content adaptation service configuration)
- Netcrave Certificate (certificate templates, profiles, and records)
"""

from .base import LDAPModel, LDAPManager
from .domains import (
    PosixGroup,
    GroupOfNames,
    GroupOfUniqueNames,
    ShadowAccount,
    PosixAccountMixin,
    InetOrgPerson,
)
from .nis import (
    PosixAccount,
    NisObject,
    IpService,
    IpProtocol,
    OncRpc,
    IpHost,
    IpNetwork,
    NisNetgroup,
    Ieee802Device,
    BootableDevice,
)
from .asterisk import (
    AsteriskExtension,
    AsteriskIAXUser,
    AsteriskSIPUser,
    AsteriskVoiceMail,
    AsteriskConfig,
)
from .openldap import Computer, RadiusClient
from .openldap_core import (
    Person,
    OrganizationalPerson,
    OrganizationalRole,
    ResidentialPerson,
    ApplicationProcess,
    Device,
    CertificationAuthority,
    PkiUser,
    DcObject,
    UidObject,
    LabeledURIObject,
    DSA,
    StrongAuthenticationUser,
    CRLDistributionPoint,
    DeltaCRL,
    DMD,
    PKICA,
)
from .powerdns import PDNSDomain, PDNSRecord
from .kerberos import (
    KrbRealmContainer,
    KrbPrincipal,
    KrbPwdPolicy,
    KrbTicketPolicy,
    KrbContainer,
    KrbKdcService,
    KrbPwdService,
    KrbAdmService,
)
from .radius import RadiusProfile
from .sendmail import SendmailMTA, SendmailMapEntry, SendmailMTAClass, SendmailMTAAlias
from .opendkim import DKIM
from .ldapns import AuthorizedServiceObject, HostObject, LoginStatusObject
from .postfix import PostfixAlias, PostfixTransport
from .icap import IcapService, IcapUser
from .certificate import CertificateTemplate, CertificateProfile, CertificateRecord, CertificateAuthority
from .corba import CorbaContainer, CorbaObject, CorbaObjectReference
from .java import JavaContainer, JavaObject, JavaSerializedObject, JavaMarshalledObject, JavaNamingReference
from .cosine import (
    PilotObject,
    PilotPerson,
    Account,
    Document,
    Room,
    Domain,
    DNSDomain,
    DomainRelatedObject,
    FriendlyCountry,
    SimpleSecurityObject,
    PilotOrganization,
)

__all__ = [
    # Base classes
    "LDAPModel",
    "LDAPManager",
    # Domains (Users and Groups)
    "PosixGroup",
    "GroupOfNames",
    "GroupOfUniqueNames",
    "ShadowAccount",
    "PosixAccountMixin",
    "InetOrgPerson",
    # NIS
    "PosixAccount",
    "NisObject",
    "IpService",
    "IpProtocol",
    "OncRpc",
    "IpHost",
    "IpNetwork",
    "NisNetgroup",
    "Ieee802Device",
    "BootableDevice",
    # Asterisk
    "AsteriskExtension",
    "AsteriskIAXUser",
    "AsteriskSIPUser",
    "AsteriskVoiceMail",
    "AsteriskConfig",
    # OpenLDAP
    "Computer",
    "RadiusClient",
    # OpenLDAP Core
    "Person",
    "OrganizationalPerson",
    "OrganizationalRole",
    "ResidentialPerson",
    "ApplicationProcess",
    "Device",
    "CertificationAuthority",
    "PkiUser",
    "DcObject",
    "UidObject",
    "LabeledURIObject",
    "DSA",
    "StrongAuthenticationUser",
    "CRLDistributionPoint",
    "DeltaCRL",
    "DMD",
    "PKICA",
    # PowerDNS
    "PDNSDomain",
    "PDNSRecord",
    # Kerberos
    "KrbRealmContainer",
    "KrbPrincipal",
    "KrbPwdPolicy",
    "KrbTicketPolicy",
    "KrbContainer",
    "KrbKdcService",
    "KrbPwdService",
    "KrbAdmService",
    # Radius
    "RadiusProfile",
    # Sendmail
    "SendmailMTA",
    "SendmailMapEntry",
    "SendmailMTAClass",
    "SendmailMTAAlias",
    # Postfix
    "PostfixAlias",
    "PostfixTransport",
    # OpenDKIM
    "DKIM",
    # LDAPNS (GSS-API, host, login status)
    "AuthorizedServiceObject",
    "HostObject",
    "LoginStatusObject",
    # Netcrave ICAP
    "IcapService",
    "IcapUser",
    # Netcrave Certificate
    "CertificateTemplate",
    "CertificateProfile",
    "CertificateRecord",
    "CertificateAuthority",
    # OpenLDAP CORBA
    "CorbaContainer",
    "CorbaObject",
    "CorbaObjectReference",
    # OpenLDAP Java
    "JavaContainer",
    "JavaObject",
    "JavaSerializedObject",
    "JavaMarshalledObject",
    "JavaNamingReference",
    # COSINE (RFC1274)
    "PilotObject",
    "PilotPerson",
    "Account",
    "Document",
    "Room",
    "Domain",
    "DNSDomain",
    "DomainRelatedObject",
    "FriendlyCountry",
    "SimpleSecurityObject",
    "PilotOrganization",
]
