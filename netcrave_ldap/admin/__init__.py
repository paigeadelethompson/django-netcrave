"""Admin configuration for netcrave LDAP models."""

# Import all admin modules to register them
from . import domains, powerdns, asterisk, openldap, radius, kerberos, sendmail, postfix, opendkim, ldapns, icap, certificate, corba, java

# Re-export admin classes for convenience
from .domains import InetOrgPersonAdmin, PosixGroupAdmin, GroupOfNamesAdmin
from .powerdns import PDNSDomainAdmin, PDNSRecordAdmin
from .asterisk import (
    AsteriskExtensionAdmin,
    AsteriskIAXUserAdmin,
    AsteriskSIPUserAdmin,
    AsteriskVoiceMailAdmin,
    AsteriskConfigAdmin,
)
from .openldap import ComputerAdmin, RadiusClientAdmin
from .radius import RadiusProfileAdmin
from .kerberos import KrbRealmContainerAdmin, KrbPrincipalAdmin, KrbPwdPolicyAdmin, KrbTicketPolicyAdmin
from .sendmail import SendmailMTAAdmin, SendmailMapEntryAdmin
from .postfix import PostfixAliasAdmin, PostfixTransportAdmin
from .opendkim import DKIMAdmin
from .ldapns import AuthorizedServiceObjectAdmin, HostObjectAdmin, LoginStatusObjectAdmin
from .icap import IcapServiceAdmin, IcapUserAdmin
from .certificate import CertificateTemplateAdmin, CertificateProfileAdmin, CertificateRecordAdmin, CertificateAuthorityAdmin
from .corba import CorbaContainerAdmin, CorbaObjectAdmin, CorbaObjectReferenceAdmin
from .java import JavaContainerAdmin, JavaObjectAdmin, JavaSerializedObjectAdmin, JavaMarshalledObjectAdmin, JavaNamingReferenceAdmin

__all__ = [
    # Domain models
    "InetOrgPersonAdmin",
    "PosixGroupAdmin",
    "GroupOfNamesAdmin",
    # PowerDNS
    "PDNSDomainAdmin",
    "PDNSRecordAdmin",
    # Asterisk
    "AsteriskExtensionAdmin",
    "AsteriskIAXUserAdmin",
    "AsteriskSIPUserAdmin",
    "AsteriskVoiceMailAdmin",
    "AsteriskConfigAdmin",
    # OpenLDAP
    "ComputerAdmin",
    "RadiusClientAdmin",
    # Radius
    "RadiusProfileAdmin",
    # Kerberos
    "KrbRealmContainerAdmin",
    "KrbPrincipalAdmin",
    "KrbPwdPolicyAdmin",
    "KrbTicketPolicyAdmin",
    # Sendmail
    "SendmailMTAAdmin",
    "SendmailMapEntryAdmin",
    # Postfix
    "PostfixAliasAdmin",
    "PostfixTransportAdmin",
    # OpenDKIM
    "DKIMAdmin",
    # LDAPNS (GSS-API, host, login status)
    "AuthorizedServiceObjectAdmin",
    "HostObjectAdmin",
    "LoginStatusObjectAdmin",
    # Netcrave ICAP
    "IcapServiceAdmin",
    "IcapUserAdmin",
    # Netcrave Certificate
    "CertificateTemplateAdmin",
    "CertificateProfileAdmin",
    "CertificateRecordAdmin",
    "CertificateAuthorityAdmin",
    # OpenLDAP CORBA
    "CorbaContainerAdmin",
    "CorbaObjectAdmin",
    "CorbaObjectReferenceAdmin",
    # OpenLDAP Java
    "JavaContainerAdmin",
    "JavaObjectAdmin",
    "JavaSerializedObjectAdmin",
    "JavaMarshalledObjectAdmin",
    "JavaNamingReferenceAdmin",
]
