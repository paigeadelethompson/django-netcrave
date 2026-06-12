"""
LDAP Models for Django-LDAP integration.
This package provides LDAP-backed Django models for managing:
- Users (inetOrgPerson + posixAccount + kerberos + radius)
- Groups (posixGroup, groupOfNames)
- Computers (device + ipHost)
- PowerDNS (dNSDomain2 + PdnsDomain/PdnsRecord)
- Asterisk (extensions, IAX/SIP endpoints, voicemail)
- Radius (radiusprofile aux, radiusClient)
- Kerberos (krbRealmContainer, krbPrincipal, policies)
- Sendmail (MTA servers, maps/aliases)
"""

from .base import LDAPModel, LDAPManager
from .domains import (
    PosixGroup,
    GroupOfNames,
    PosixAccountMixin,
    InetOrgPerson,
)
from .asterisk import (
    AsteriskExtension,
    AsteriskIAXUser,
    AsteriskSIPUser,
    AsteriskVoiceMail,
    AsteriskConfig,
)
from .nis import NisObject
from .openldap import Computer, RadiusClient
from .powerdns import PDNSDomain, PDNSRecord
from .kerberos import (
    KrbRealmContainer,
    KrbPrincipal,
    KrbPwdPolicy,
    KrbTicketPolicy,
)
from .radius import RadiusProfile
from .sendmail import SendmailMTA, SendmailMapEntry
from .postfix import PostfixAlias, PostfixTransport
__all__ = [
    # Base classes
    "LDAPModel",
    "LDAPManager",
    # Domains (Users and Groups)
    "PosixGroup",
    "GroupOfNames",
    "PosixAccountMixin",
    "InetOrgPerson",
    # Asterisk
    "AsteriskExtension",
    "AsteriskIAXUser",
    "AsteriskSIPUser",
    "AsteriskVoiceMail",
    "AsteriskConfig",
    # NIS
    "NisObject",
    # OpenLDAP
    "Computer",
    "RadiusClient",
    # PowerDNS
    "PDNSDomain",
    "PDNSRecord",
    # Kerberos
    "KrbRealmContainer",
    "KrbPrincipal",
    "KrbPwdPolicy",
    "KrbTicketPolicy",
    # Radius
    "RadiusProfile",
    # Sendmail
    "SendmailMTA",
    "SendmailMapEntry",
    # Postfix
    "PostfixAlias",
    "PostfixTransport",
]
