# TODO: Netcrave LDAP Project

## Overview
This project provides LDAP-backed Django models for managing:
- Users (inetOrgPerson + posixAccount + kerberos + radius)
- Groups (posixGroup, groupOfNames)
- Computers (device + ipHost)
- PowerDNS (dNSDomain2 + PdnsDomain/PdnsRecord)
- Asterisk (extensions, IAX/SIP endpoints, voicemail)
- Radius (radiusprofile aux, radiusClient)
- Kerberos (krbRealmContainer, krbPrincipal, policies)
- Sendmail (MTA servers, maps/aliases)
- Postfix (mail aliases, transport maps)

**All models are now implemented in `netcrave_ldap/` app.**

**IMPORTANT: All Django models MUST conform to the LDAP schemas in `schemas/`.**
Always check the schema files before adding fields. The schema defines:
- Required attributes (`MUST`) vs optional attributes (`MAY`)
- Syntax constraints (integer, IA5String, UTF-8 string, etc.)
- Equality and substring matching rules
- Single-value vs multi-value

**IMPORTANT: Viewing data in LDAP is just as important as creating/modifying it.**
The admin interface should provide comprehensive read access:
- Clear table views with sortable columns
- Drill-down to individual entries
- Filterable lists (by name, type, OU, etc.)
- Breadcrumb navigation showing the DN hierarchy
- Batch operations for bulk viewing/export

---

## Priority Improvements

### Field Descriptions & Documentation
Each model field MUST have:
- [x] Clear `help_text` explaining what the field does
- [x] Valid LDAP schema reference (e.g., "RFC2798: inetOrgPerson")
- [x] Default value documentation
- [x] Constraints/validations noted
- [x] Example values for complex fields
- [x] Syntax type matching the schema definition

### Auto-Increment IDs
User and group IDs (uidNumber, gidNumber) should auto-increment from a dedicated counter object in LDAP to avoid conflicts. **Never require users to enter DNs** - Django must handle all DN construction automatically based on configuration.

### Schema Compliance Verification
Before implementing any model:
- [x] Check `schemas/` for the appropriate schema file
- [x] Identify required (`MUST`) and optional (`MAY`) attributes
- [x] Match syntax types correctly (integer, IA5String, UTF-8 string, etc.)
- [x] Respect single-value vs multi-value constraints

---

## Admin Interface Requirements

### Viewing Data (Equally Important as Writing)

The Django admin should provide comprehensive read access to LDAP data:

| Feature | Description |
|---------|-------------|
| Clear table views | All model lists show relevant fields in columns |
| Sortable columns | Click column headers to sort by any field |
| Filterable lists | Filters for name, type, OU, status, etc. |
| Drill-down navigation | Click entries to see full details |
| DN hierarchy display | Breadcrumbs showing LDAP path (e.g., `dc=example,dc=com > ou=users`) |
| Search across fields | Global search across common attributes |
| Export functionality | Bulk export as CSV/JSON for external tools |

### Common Admin Patterns
- [x] List page with search, filters, pagination
- [x] Detail view showing all LDAP attributes
- [x] Related entries browser (e.g., see all members of a group)
- [x] Audit trail showing last modification time/source

### Organizational Unit Management
- [x] Create new OUs under existing containers
- [x] Move objects between OUs (drag-and-drop or action menu)
- [x] Copy objects to new locations (with DN regeneration)
- [x] Rename OUs (with recursive DN updates for children)
- [x] View OU hierarchy as a tree view

### Admin Actions
- [x] **Move to OU**: Select an object and choose a target OU from dropdown
- [x] **Create sub-OU**: From an OU detail page, create nested OUs
- [x] **Bulk move**: Select multiple objects to move under a new parent

---

## 1. Users Model & Admin

### Models
- [x] `InetOrgPerson` - primary user model with:
  - **Basic** (inetOrgPerson core): cn, sn (surname), uid, mail, givenName, displayName
  - **Org** (inetOrgPerson): title, ou (organizationalUnitName), departmentNumber, employeeNumber, employeeType
  - **Contact**: telephoneNumber, mobile, homePhone, pager, facsimileTelephoneNumber
  - **POSIX** (posixAccount - auxiliary): uidNumber (auto-increment), gidNumber (auto-increment from default or specified group), loginShell, gecos, shadowLastChange, shadowMin, shadowMax, shadowWarning, shadowInactive, shadowExpire, shadowFlag
  - **Kerberos** (krbPrincipalAux - auxiliary): krbPrincipalName, krbCanonicalName, krbPasswordExpiration, krbPrincipalExpiration, krbPwdPolicyReference, krbTicketPolicyReference, krbUPEnabled, krbLastSuccessfulAuth, krbLastFailedAuth, krbLoginFailedCount
  - **RADIUS** (radiusprofile - auxiliary): radiusAuthType, radiusFramedIPAddress, radiusServiceType, radiusSessionTimeout, radiusIdleTimeout, radiusSimultaneousUse

### Admin
- [x] List display: cn, uid, mail, displayName, ou
- [x] Search: cn, sn, uid, mail
- [x] Fieldsets:
  - Identity (cn, sn, uid, mail, givenName, displayName)
  - Organization (title, ou, departmentNumber, employeeNumber, employeeType)
  - Contact (telephoneNumber, mobile, homePhone, pager, facsimileTelephoneNumber)
  - POSIX Account (uidNumber, gidNumber, loginShell, gecos)
  - Kerberos (krbPrincipalName, policy reference, status flags)
  - RADIUS (auth type, framed IP, service type)

### Defaults
- [x] uidNumber: auto-increment from counter object (starting at 1000)
- [x] gidNumber: auto-increment or from group (starting at 100)
- [x] loginShell: /bin/bash
- [x] shadowLastChange: today ( LDAPmodify timestamp )
- [x] krbUPEnabled: TRUE

---

## 2. Groups Model & Admin

### Models
- [x] `PosixGroup` - POSIX group:
  - cn (group name), gidNumber (auto-increment), memberUid (list of UIDs), description, userPassword
  - Schema: nis.schema - posixGroup STRUCTURAL
- [x] `GroupOfNames` - general group:
  - cn, member (DNs - must be complete DNs), description, ou, o, userPassword
  - Schema: core.schema - groupOfNames STRUCTURAL

### Admin
- [x] List display: cn, gidNumber/member count, description
- [x] Search: cn, description
- [x] Fieldsets for each model
- [x] User selector widget to add members (auto-constructs DNs)

### Defaults
- [x] gidNumber: auto-increment from counter object (starting at 100)
- [x] memberUid: empty list

---

## 3. Computers Model & Admin

### Models
- [x] `Computer` - device + ipHost:
  - cn (hostname), ipHostNumber (list of IPs), description, macAddress
  - Derived from ieee802Device aux class for MAC
  - Schema: core.schema - device STRUCTURAL + ipHost AUXILIARY

### Admin
- [x] List display: cn, ipHostNumber, description
- [x] Search: cn, ipHostNumber, macAddress
- [x] Fieldsets:
  - Identity (cn)
  - Network (ipHostNumber, macAddress)
  - Description

---

## 4. PowerDNS Model & Admin

### Models
- [x] `PDNSDomain` - DNS zone with template support:
  - domainComponent (zone name - e.g., "example.com"), dNSTTL (default TTL for records),
    pdnsDomainType (master/slave/secondary), master_ips, soaRecord, nsRecords
  - object_classes: dNSDomain2, domain, PdnsDomain (from dnsdomain2.schema)
  - **Template System**: domain templates with default SOA/NS configuration

- [x] `PDNSRecord` - DNS record:
  - domainComponent (FQDN or relative name), dNSTTL (can inherit from zone),
    type-specific fields validated by record type
  - object_classes: dNSDomain2, PdnsRecordData
  - **RRSet Support**: Multiple records with same name/type treated as a set

### Admin
- [x] PDNSDomain:
  - Zone name field (auto-appended to base DNS OU), default TTL setting,
    domain type (master/slave/secondary), master IPs for slaves,
    SOA/NS editing with template preview
  - Domain templates browser/copy feature
- [x] PDNSRecord:
  - Zone selector, Host (relative to zone), Type (dropdown), Value,
    TTL (inherit or override), Priority (for MX/SRV)
  - Type-specific value validation and examples
- [x] Auto-create zone records from templates on domain creation

### Defaults
- [x] dNSTTL: from settings or zone template (default 3600)
- [x] pdnsDomainType: master
- [x] pdnsDomainId: auto-incrementing

---

## DNS Record Types & Validation

Based on `schemas/powerdns/dnsdomain2.schema`:

| Type | Value Format | Required Fields | Example |
|------|-------------|-----------------|---------|
| A | IPv4 address (IPv4Address syntax) | - | 192.0.2.1 |
| AAAA | IPv6 address (IPv6Address syntax) | - | 2001:db8::1 |
| CNAME | FQDN | target must be valid FQDN | www.example.com. |
| MX | priority (0-65535) + FQDN | priority, exchange | 10 mail.example.com. |
| NS | FQDN | authoritative nameserver | ns1.example.com. |
| PTR | FQDN (reverse lookup target) | - | www.example.com. |
| TXT | string(s) (IA5String, may be quoted) | - | "v=spf1 include:_spf.example.com ~all" |
| SPF | string (same as TXT) | - | "v=spf1 ... " |
| SOA | MNAME + RNAME + serial + refresh + retry + expire + min TTL | all fields required | see below |
| SRV | priority + weight + port + FQDN | all numeric fields | _ldap._tcp.example.com. 0 5 389 ldap.example.com. |
| CAA | flags (0-255) + tag + value | issue/issuewild/tag | 0 issue "letsencrypt.org" |
| DNSKEY | flags (0-65535) + protocol (0-255) + algorithm + public key | all fields | see below |
| DS | keytag + algorithm + digest type + digest | all fields | 12345 8 2 1234... |
| NSEC | owner + types bitmap | - | see RFC 3755 |
| RRSIG | type covered + algorithm + labels + orig TTL + expire + sign exp + key tag + signer + signature | all fields | see RFC 3755 |
| NAPTR | order + preference + flags + services + regex + replacement | all fields | 100 10 "S" "E2U+sip" "!^.*$!sip:user@example.com!" . |
| SSHFP | algorithm + type + fingerprint | all fields | 1 1 abcd1234... |
| TLSA | usage + selector + matching type + cert data | all fields | 0 0 1 abcd... |
| CERT | certificate type + key tag + algorithm + cert data | all fields | see RFC 4398 |

### SOA Record Fields
```
primary: FQDN of primary nameserver (MUST)
hostmaster: email (replaces @ with .) (MUST)
serial: integer, zone version (auto-increment or date format) (MUST)
refresh: integer, seconds between AXFR checks (MUST) (default 3600)
retry: integer, seconds after failed refresh (MUST) (default 900)
expire: integer, seconds before zone is considered stale (MUST) (default 604800)
minimum: integer, minimum TTL for negative responses (MUST) (default 86400)
```

### DNSSEC Support
Based on schemas/powerdns/dnsdomain2.schema:
- [x] DNSSEC signing configuration per domain
- [x] DS record management (delegation signer)
- [x] DNSKEY record generation/management
- [x] RRSIG record display (read-only, auto-generated)
- [x] NSEC/NSEC3 parameters configuration
- [x] Key rollover support

### Schema Field Definitions
```python
# From dnsdomain2.schema:
dNSTTL - integer, time to live in seconds
dNSClass - IA5String (IN for Internet)
aRecord - IPv4Address syntax
a6Record - IPv6Address syntax (deprecated, use AAAA)
aaaaRecord - IPv6Address syntax
aFSDBRecord - IA5String (AFS database location)
aPLRecord - IA5String (address prefix list)
aRSNAPeerRecord - IA5String
cDSRecord - IA5String (child DS record)
certRecord - IA5String (certificate data)
dHCIDRecord - IA5String (DHCID data)
dNameRecord - IA5String (alias for entire subtree)
dNSKeyRecord - IA5String (DNS public key)
dNSSECKeyData - IA5String
dSRecord - IA5String (delegation signer)
gPosRecord - IA5String (geographical position)
hInfoRecord - IA5String (host information)
iPSecKeyRecord - IA5String (IPSec key)
kXRecord - IA5String (key exchange)
KeyRecord - IA5String (DNSSEC key - use DNSKEY instead)
locRecord - IA5String (location data)
mInfoRecord - IA5String (mail list info)
mxRecord - IA5String (mail exchange)
nAPTRRecord - IA5String (name authority pointer)
nXTRecord - IA5String (next name - deprecated, use NSEC)
nSEC3ParamRecord - IA5String
nSEC3Record - IA5String (NSEC version 3)
nSECRecord - IA5String (secure negative response)
pTRRecord - IA5String (pointer record)
rRSIGRecord - IA5String (RRSIG data)
rPRecord - IA5String (responsible person)
sSHFPRecord - IA5String (SSH fingerprint)
SigRecord - IA5String (signature - use RRSIG instead)
sRVRecord - IA5String (service location)
tLSARecord - IA5String (TLSA certificate association)
tXTRecord - IA5String (text record)
wKSRecord - IA5String (well known services)
```

---

## 5. Asterisk Model & Admin

### Models
- [x] `AsteriskExtension` - base dialplan entry:
  - cn, astContext, astExtension, astPriority, astApplication, astApplicationData
  - Schema: asterisk.schema - AsteriskExtension STRUCTURAL
- [x] `AsteriskIAXUser` - IAX endpoint (extends extension):
  - All extension fields + astAccountName, astMD5secret, astAccountHost,
    astPort, astUsername, astAuthType, astAccountType, astAccountCallerID,
    astAccountDisallowedCodec, astAccountAllowedCodec
- [x] `AsteriskSIPUser` - SIP endpoint (extends extension):
  - All extension fields + astAccountName, astAccountSecret, astAccountNAT,
    astTransport, astCodecs, astAllow, astDirectMedia, astAccountCallLimit,
    astAccountVideoSupport, astAccountLanguage
- [x] `AsteriskVoiceMail` - voicemail:
  - cn, astContext, astVoicemailMailbox, astVoicemailPassword,
    astVoicemailFullname, astVoicemailEmail, astVoicemailPager
- [x] `AsteriskConfig` - configuration entries for global settings

### Admin
- [x] Extension: context dropdown, extension number, priority, application
  dropdown with parameters (Dial, PlayTones, VoiceMail, etc.)
- [x] IAX User: identity (name/secret), network (host/port), context,
  authentication type, codec settings
- [x] SIP User: identity (name/secret/password), NAT settings, transport
  (UDP/TCP/TLS), codec settings, call limit
- [x] Voicemail: mailbox number (auto-generated or manual), password
  (generate button?), fullname, email notifications, pager

### Defaults
- [x] astContext: default
- [x] astPriority: 1
- [x] astApplication: Dial
- [x] astAccountNAT: force_rport,comedia (SIP)
- [x] astVoicemailPassword: auto-generated or configurable from settings
- [x] astAccountTransport: udp

---

## 6. Radius Model & Admin

### Models
Based on schemas/freeradius/radius.schema:
- [x] `RadiusProfile` - user RADIUS profile (auxiliary on inetOrgPerson):
  - radiusAuthType (PAP/CHAP/MSCHAPv2), radiusPasswordRetry, radiusServiceType
  - radiusFramedIPAddress, radiusFramedIPNetmask, radiusFramedMTU
  - radiusSessionTimeout, radiusIdleTimeout, radiusSimultaneousUse,
    radiusClass, radiusCallingStationId, radiusFilterId, radiusCallbackNumber,
    radius CallbackId, radius FramedCompression, radiusFramedProtocol,
    radiusFramedRoute, radiusFramedRouting, radiusNASIPAddress
- [x] `RadiusClient` - NAS/AP registration:
  - radiusClientIdentifier (IP or hostname), radiusClientSecret,
    radiusClientShortname, radiusClientType, radiusClientComment,
    radiusClientVirtualServer

### Admin
- [x] RadiusProfile:
  - Authentication (auth type dropdown, password retry limit, service type)
  - Framed IP (IP address, netmask, MTU, protocol, routing)
  - Session (timeout in seconds, simultaneous use limit, idle timeout)
  - Helper button to add radiusProfile aux class when fields populated
- [x] RadiusClient:
  - Client ID (IP/hostname), Secret (generate button with copy-to-clipboard),
    shortname, type dropdown, comments

### Defaults
- [x] radiusAuthType: PAP
- [x] radiusServiceType: Framed-User
- [x] radiusPasswordRetry: 3
- [x] radiusSessionTimeout: 3600
- [x] radiusSimultaneousUse: 1
- [x] radiusFramedMTU: 1500

### Schema Fields (from freeradius.schema)
```
radiusAuthType - IA5String (PAP, CHAP, MSCHAP, MSCHAPV2, etc.)
radiusArapFeatures - IA5String
radiusArapSecurity - IA5String
radiusArapZoneAccess - IA5String
radiusCallbackId - IA5String
radiusCallbackNumber - IA5String
radiusCalledStationId - IA5String
radiusCallingStationId - IA5String
radiusClass - IA5String (multiple)
radiusClientIdentifier - IA5String (IP or hostname)
radiusClientSecret - IA5String
radiusClientShortname - IA5String
radiusClientVirtualServer - IA5String
radiusClientType - IA5String
radiusClientRequireMa - BOOLEAN
radiusClientComment - IA5String
radiusFramedIPAddress - IA5String
radiusFramedIPNetmask - IA5String
radiusFramedProtocol - IA5String (PPP, SLIP)
radiusFramedRouting - IA5String (none, broadcast, rip)
radiusFramedMTU - INTEGER
radiusFramedCompression - IA5String (Van Jacobson TCP/IP, VFCOMPRESS)
radiusFilterId - IA5String
radiusIdleTimeout - INTEGER
radiusNASIPAddress - IA5String
radiusNASIdentifier - IA5String
radiusNASPort - INTEGER
radiusNASPortType - IA5String (Ethernet, TokenRing, etc.)
radiusSessionTimeout - INTEGER
radiusSimultaneousUse - INTEGER
```

---

## 7. Kerberos Model & Admin

### Models
Based on schemas/krb5/kerberos.schema:
- [x] `KrbRealmContainer` - realm configuration:
  - cn, krbUPEnabled, krbLdapServers (list of DNs),
    krbSupportedEncSaltTypes, krbTicketPolicyReference,
    krbPwdPolicyReference, krbKdcServers, krbPwdServers, krbAdmServers
  - Schema: krb5.schema - krbRealmContainer STRUCTURAL
- [x] `KrbPrincipal` - principal entry:
  - krbPrincipalName (required), krbCanonicalName, krbUPEnabled
  - krbPrincipalExpiration, krbPasswordExpiration, krbLoginFailedCount,
    krbLastSuccessfulAuth, krbLastFailedAuth
  - krbTicketPolicyReference, krbPwdPolicyReference, krbTicketFlags,
    krbAllowedToDelegateTo, krbPrincipalAuthInd
- [x] `KrbPwdPolicy` - password policy:
  - cn, krbMaxPwdLife (7776000 = 90 days), krbMinPwdLife (86400 = 1 day),
    krbPwdMinLength (min 8), krbPwdMaxFailure (5), krbPwdLockoutDuration,
    krbPwdHistoryLength
- [x] `KrbTicketPolicy` - ticket policy:
  - cn, krbMaxTicketLife (86400 = 24 hours), krbMaxRenewableAge (604800 = 7 days),
    krbTicketFlags

### Admin
- [x] Realm: server DNs (KDC/PWD/ADM), policies, encryption types multiselect
- [x] Principal: name (required), status flags, expiration dates,
  policy references, force password change toggle
- [x] Password Policy: max life, min length, max failures, lockout duration,
  history length
- [x] Ticket Policy: max ticket life, renewable age, ticket flags checkboxes

### Defaults
- [x] krbUPEnabled: TRUE
- [x] krbMaxPwdLife: 7776000 (90 days)
- [x] krbMinPwdLife: 86400 (1 day)
- [x] krbPwdMinLength: 8
- [x] krbPwdMaxFailure: 5
- [x] krbPwdLockoutDuration: 900 (15 minutes)
- [x] krbMaxTicketLife: 86400 (24 hours)
- [x] krbMaxRenewableAge: 604800 (7 days)

### Schema Fields (from krb5.schema)
```
krbContainer - STRUCTURAL, MUST cn
krbRealmContainer - STRUCTURAL, MUST cn, MAY various policy refs
krbPrincipalAux - AUXILIARY, MAY principal attributes
krbPrincipal - STRUCTURAL, MUST krbPrincipalName
krbTicketPolicyAux - AUXILIARY, MAY ticket policy attrs
krbTicketPolicy - STRUCTURAL, MUST cn

Attributes:
krbContainerReference - DN (references container)
krbRealmReferences - DN (realm reference)
krbLdapServers - IA5String (LDAP URI list)
krbSupportedEncSaltTypes - IA5String
krbDefaultEncSaltTypes - IA5String
krbTicketPolicyReference - DN
krbPwdPolicyReference - DN
krbKdcServers - DN (list)
krbPwdServers - DN (list)
krbAdmServers - DN (list)

krbPrincipalName - IA5String (required, primary identifier)
krbCanonicalName - IA5String
krbUPEnabled - BOOLEAN
krbPrincipalExpiration - generalizedTime
krbPasswordExpiration - generalizedTime
krbLoginFailedCount - INTEGER
krbLastSuccessfulAuth - generalizedTime
krbLastFailedAuth - generalizedTime
krbTicketFlags - INTEGER (bit flags)
krbMaxTicketLife - INTEGER
krbMaxRenewableAge - INTEGER

krbPrincipalType - INTEGER (user=1, service=2, etc.)
krbExtraData - OCTET STRING
krbAllowedToDelegateTo - IA5String (list of services)
krbPrincipalAuthInd - IA5String (authentication indicators)

krbPwdPolicy:
krbMaxPwdLife - INTEGER
krbMinPwdLife - INTEGER
krbPwdMinLength - INTEGER
krbPwdMinDiffChars - INTEGER
krbPwdHistoryLength - INTEGER
krbPwdMaxFailure - INTEGER
krbPwdFailureCountInterval - INTEGER
krbPwdLockoutDuration - INTEGER
```

---

## 8. PKI / Certificate Models

### Based on core.schema and other RFCs:
- [x] `X509Certificate` - X.509 certificate storage:
  - userCertificate (X.509, DER-encoded)
  - cACertificate (CA certificate)
  - authorityRevocationList (ARL)
  - certificateRevocationList (CRL)
  - crossCertificatePair
- [x] `PKIUser` - User with certificates:
  - User of inetOrgPerson + PKIX attributes

---

## Relationships Between Models

Django should handle all LDAP DN relationships automatically. Here are the expected relationships:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Realm Container                              │
│                    (krbRealmContainer)                              │
│  - Defines Kerberos realm configuration                             │
│  - References: KDC/PWD/ADM servers                                  │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 ├─»─ krbTicketPolicyReference ─»─┐
                 │                                │
                 └─»─ krbPwdPolicyReference ──────┼─»─ Password Policy
                                                  │   (krbPwdPolicy)
                                                  └─»─ Ticket Policy
                                                      (krbTicketPolicy)

┌─────────────────────────────────────────────────────────────────────┐
│                        Kerberos Principal                            │
│                       (krbPrincipal)                                 │
│  - User/Service identity in Kerberos                                │
│  - May reference: realm container, policies                         │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 ├─»— memberOf —» GroupOfNames ─» POSIXGroup (indirect)
                 │     (via groupOfNames.member)        (via memberUid)
                 │
                 └─»— krbAllowedToDelegateTo ─» Service Principals

┌─────────────────────────────────────────────────────────────────────┐
│                         User Account                                 │
│                    (inetOrgPerson + posixAccount)                   │
│  - Human user or service account                                    │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 ├─»— uidNumber ───────────────────┐
                 │     (auto-increment counter)    │
                 │                                │
                 └─»— memberOf ──────────────────┼─»─ POSIXGroup
                        (via groupOfNames.member)   (gidNumber match)
                        or posixGroup.memberUid

┌─────────────────────────────────────────────────────────────────────┐
│                          DNS Zone                                    │
│                       (dNSDomain2 + PdnsDomain)                     │
│  - DNS zone/region                                                  │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 ├─»— NS records ─»─ Other PDNSDomains (delegations)
                 │     (refers to other zones)
                 │
                 └─»— SOA record ──» Primary nameserver (FQDN)

┌─────────────────────────────────────────────────────────────────────┐
│                       Radius Client                                  │
│                      (radiusClient)                                  │
│  - NAS/AP device registered for RADIUS                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     Asterisk Configuration                           │
│                  (various Asterisk objectClasses)                   │
│  - Dialplan, SIP/IAX endpoints, Voicemail                           │
│  - May reference users (by uid or mail)                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Installable Package (pyproject.toml)

The project is configured as an installable Python package:

```bash
# Install in editable mode for development
pip install -e .

# Or build and install
pip build .
pip install ldap_management-0.1.0-py3-none-any.whl
```

### Command Line Interface

After installation, use `netcrave` instead of `manage.py`:

```bash
# Initialize the LDAP tree
netcrave init_tree

# Create a new superuser
netcrave createsuperuser

# Run the development server
netcrave runserver

# Other Django management commands still available:
netcrave migrate
netcrave collectstatic

# Generate configuration interactively
netcrave config
```

### pyproject.toml Configuration

```toml
[tool.poetry]
name = "django-ldap"
version = "0.1.0"
description = "Django application for managing LDAP infrastructure"
authors = [{ name = "Admin", email = "admin@example.com" }]
readme = "README.md"

packages = [
    { include = "netcrave" },
    { include = "netcrave_ldap" },
    { include = "netcrave_ca" },
]

[tool.poetry.dependencies]
python = "^3.9"
django = "^4.2"
python-ldap = { path = "3rdparty/python-ldap" }

[tool.poetry.scripts]
netcrave = "netcrave.cli:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### netcrave/cli.py Entry Point

```python
# netcrave/cli.py
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "netcrave.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)
```

---

## Settings to Add

```python
# LDAP Base DNs for each subtree
# Django will automatically construct full DNs based on these
LDAP_BASE_DN = "dc=example,dc=com"

LDAP_OU_USERS = "ou=users"
LDAP_OU_GROUPS = "ou=groups"
LDAP_OU_COMPUTERS = "ou=computers"
LDAP_OU_DNS = "ou=dns"
LDAP_OU_AST = "ou=asterisk"
LDAP_OU_RADIUS = "ou=radius"
LDAP_OU_KRB = "ou=kerberos"

# Auto-increment counter configuration
LDAP_COUNTER_BASE_DN = "cn=counters," + LDAP_BASE_DN
LDAP_UID_COUNTER_ATTR = "uidNumberCounter"
LDAP_GID_COUNTER_ATTR = "gidNumberCounter"

# Default values for auto-increment counters (stored in LDAP)
LDAP_DEFAULT_UID_NUMBER = 1000
LDAP_DEFAULT_GID_NUMBER = 100

# POSIX defaults
LDAP_DEFAULT_LOGIN_SHELL = "/bin/bash"
LDAP_DEFAULT_HOME_BASE = "/home"
LDAP_DEFAULT_GECOS = "System User"

# DNS defaults
LDAP_DEFAULT_DNS_TTL = 3600
LDAP_DEFAULT_SOA_SERIAL = "%Y%m%d01"  # Date-based format: 2024010101
LDAP_DEFAULT_SOA_REFRESH = 3600
LDAP_DEFAULT_SOA_RETRY = 900
LDAP_DEFAULT_SOA_EXPIRY = 604800
LDAP_DEFAULT_SOA_MIN_TTL = 86400

# Asterisk defaults
ASTERISK_DEFAULT_CONTEXT = "default"
ASTERISK_DEFAULT_PRIORITY = 1
ASTERISK_DEFAULT_TRANSPORT = "udp"

# RADIUS defaults
RADIUS_DEFAULT_AUTH_TYPE = "PAP"  # PAP, CHAP, MSCHAPV2
RADIUS_DEFAULT_SERVICE_TYPE = "Framed-User"
RADIUS_DEFAULT_PASSWORD_RETRY = 3
RADIUS_DEFAULT_SESSION_TIMEOUT = 3600
RADIUS_DEFAULT_SIMULTANEOUS_USE = 1
RADIUS_DEFAULT_FRAMED_MTU = 1500

# Kerberos defaults
KRB_DEFAULT_MAX_PWD_LIFE = 7776000      # 90 days
KRB_DEFAULT_MIN_PWD_LIFE = 86400        # 1 day
KRB_DEFAULT_PWD_MIN_LENGTH = 8
KRB_DEFAULT_PWD_MAX_FAILURE = 5
KRB_DEFAULT_PWD_LOCKOUT_DURATION = 900  # 15 minutes
KRB_DEFAULT_TICKET_LIFETIME = 86400     # 24 hours
KRB_DEFAULT_RENEWABLE_AGE = 604800      # 7 days

# Password generation settings
PASSWORD_GENERATION_ENABLED = True
DEFAULT_PASSWORD_LENGTH = 16
DEFAULT_PASSWORD_INCLUDE_SYMBOLS = True

# UI/UX settings
ADMIN_LIST_PAGE_SIZE = 25
LDAP_SEARCH_SUGGESTION_LIMIT = 50

# Schema validation settings
SCHEMA_VALIDATION_ENABLED = True  # Validate against schemas/ before save

```

---

## Django Management Commands

All LDAP management should be done as Django management commands in `ldap_admin/management/commands/`:

| Command | Description |
|---------|-------------|
| `init_tree` | Initialize base LDAP structure (OUs, counters, default policies) |
| `delete_tree` | Safely delete LDAP entries with dependency checks |
| `backup_ldap` | Backup LDAP database to LDIF or JSON format |
| `ldap_info` | Display LDAP tree structure, entry counts, schema info |

### Command Structure

```python
# netcrave/management/commands/init_tree.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Initialize the LDAP directory tree"
    
    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--skip-defaults", action="store_true")
    
    def handle(self, *args, **options):
        # Implementation
```

### Available Commands

**init_tree**
```bash
# Initialize the LDAP tree with default structure
netcrave init_tree

# Preview what would be created without making changes
netcrave init_tree --dry-run

# Initialize without creating sample data
netcrave init_tree --skip-defaults
```

**delete_tree**
```bash
# Safely delete all entries under an OU
netcrave delete_tree ou=users,dc=example,dc=com

# Preview deletions first
netcrave delete_tree <dn> --dry-run

# Soft-delete (move to cn=deleted)
netcrave delete_tree <dn> --soft-delete
```

**backup_ldap**
```bash
# Backup entire LDAP directory
netcrave backup_ldap /path/to/backup.ldif

# Backup as JSON for Django restore
netcrave backup_ldap /path/to/backup.json --format=json
```

**ldap_info**
```bash
# Show LDAP tree structure
netcrave ldap_info

# Show entry counts per OU
netcrave ldap_info --counts

# Show schema information
netcrave ldap_info --schema
```

---

## Additional Notes

### DN Construction (Automatic - User Should Never See DNs)
- Users: `{LDAP_OU_USERS},{LDAP_BASE_DN}`
- Groups: `{LDAP_OU_GROUPS},{LDAP_BASE_DN}`
- DNS: `{LDAP_OU_DNS},{LDAP_BASE_DN}`
- Kerberos: `{LDAP_OU_KRB},{LDAP_BASE_DN}`

### Counter Objects (for Auto-Increment)
```python
# LDAP entry for UID counter:
dn: cn=uidNumber,{LDAP_COUNTER_BASE_DN}
objectClass: simpleSecurityObject
cn: uidNumber
userPassword: {SSHA}...
```

### Model Relationships in Django
Use `ForeignKey` or `ManyToManyField` to represent relationships. The admin should show dropdowns with human-readable names, not DNs.

```python
# Example: Principal -> Realm relationship
class KrbPrincipal(models.Model):
    realm = models.ForeignKey('KrbRealmContainer', on_delete=models.PROTECT)
    # Django handles: cn=principal,ou=users,ou=kerberos,dc=example,dc=com

# Example: Group -> Member relationship  
class PosixGroup(models.Model):
    members = models.ManyToManyField('InetOrgPerson', related_name='groups')
    # Django handles memberUid attribute with just the uid value
```

---

## 8. Sendmail Model & Admin

### Models
Based on `schemas/sendmail/sendmail.schema`:
- [ ] `SendmailMTA` - MTA server configuration:
  - cn, sendmailMTACluster (cluster name), sendmailMTAHost (hostname)
  - Schema: sendmailMTA STRUCTURAL, may include description
- [ ] `SendmailMapEntry` - map/alias entries:
  - sendmailMTAMapName (map identifier), sendmailMTAKey (left side),
    sendmailMTAMapValue (right side), sendmailMTAMapSearch (recursive flag)
  - Schema: sendmailMTAMap STRUCTURAL, must have cn, nisMapName, nisMapEntry

### Admin
- [ ] MTA: Cluster selector, hostname field, description
- [ ] Map Entry: Map name dropdown (aliases, transport, generic), key field,
  value field with type-specific format validation
- [ ] Search by map name, key pattern, or value

---

## 9. Postfix Model & Admin

### Models
Postfix uses standard LDAP schema for mail routing:
- [x] `PostfixAlias` - mail aliases:
  - mail (recipient email), destination (destination address/addresses)
  - Based on inetOrgPerson/mailRoutingAddress attributes
- [x] `PostfixTransport` - transport maps:
  - mailRoutingDomain, transportType, transportNextHop
  - Schema: Standard mail schema attributes

### Admin
- [x] Alias: Email address field, destination field (single or multiple),
  description
- [x] Transport: Domain pattern, transport type dropdown (smtp, local, virtual),
  next hop host/port
- [x] Bulk import/export for maps as text files

---

## Project Structure

### Current Multi-App Architecture (Completed)
The project uses a clean multi-app structure under `netcrave/`:

```
netcrave/
├── __init__.py
├── cli.py              # Main entry point for 'netcrave' command
├── settings.py         # Shared Django settings
├── urls.py             # Root URL configuration
├── wsgi.py
├── manage.py           # Convenience wrapper
└── management/
    └── commands/
        ├── config.py       # Interactive configuration generator
        └── init_tree.py    # Initialize LDAP directory tree

netcrave_ldap/          # LDAP-backed models app
├── models/             # User, Group, Computer, PowerDNS, Asterisk, RADIUS, Kerberos
├── admin/
├── utils/
└── migrations/

netcrave_ca/            # Certificate Authority app (new)
├── models/
├── admin/
├── utils/
└── migrations/
```

**Key changes from previous structure:**
- `netcrave/` is now the main project package containing shared configuration
- `netcrave_ldap/`, `netcrave_ca/` are separate Django apps
- CLI command is `netcrave` (not `dldap` or `netcrave-ldap`)
- pyproject.toml defines: `netcrave = "netcrave.cli:main"`

---

## Additional Notes
