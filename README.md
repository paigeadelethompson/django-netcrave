# Netcrave LDAP Management

Django application for managing comprehensive LDAP infrastructure including users, groups, DNS, Asterisk telephony, RADIUS authentication, Kerberos identity management, PKI/Certificate Authority, ICAP proxy integration, OpenDKIM email signing, and more.

## Features

### Core Directory Services
- **Users** (inetOrgPerson + posixAccount + kerberos + radius) - Full user lifecycle management with POSIX accounts, Kerberos principals, and RADIUS attributes
- **Groups** (posixGroup, groupOfNames) - POSIX groups and general purpose groups with member management
- **Computers** (device + ipHost + ieee802Device) - Network device registration with IP/MAC tracking

### Networking & DNS
- **PowerDNS** (dNSDomain2 + PdnsDomain/PdnsRecord) - Full DNS zone and record management with DNSSEC support
  - A, AAAA, CNAME, MX, NS, PTR, TXT, SPF records
  - SOA record configuration with auto-incrementing serials
  - DNSSEC: DS, DNSKEY, RRSIG, NSEC record types

### Telephony (Asterisk)
- **Extensions** (dialplan entries) - Asterisk dialplan configuration with context support
- **SIP/IAX Endpoints** - VoIP endpoint configuration with codec settings, NAT traversal
- **Voicemail** - Mailbox management with email notifications and pager integration

### Authentication & Security
- **RADIUS** (freeradius schema) - NAS/AP client registration and user RADIUS profiles
  - Authentication types: PAP, CHAP, MSCHAPv2
  - Framed IP addressing, session timeouts, rate limiting
- **Kerberos** (krb5.schema) - Complete Kerberos infrastructure
  - Realm containers with KDC/PWD/ADM server references
  - Principal management with expiration and policy control
  - Password policies (length, max failures, lockout duration)
  - Ticket policies (lifetime, renewable age)

### PKI / Certificate Authority
- **Certificate Storage** (userCertificate, cACertificate, CRL) - X.509 certificate management in LDAP
- **Certificate Templates** - Define reusable certificate configurations (validity, key size, key usage)
- **Certificate Profiles** - Map hostnames to templates for ACME automated issuance
- **Certificate Records** - Store issued certificates with metadata (status, revocation info, storage paths)
- **Certificate Authority** - CA configuration and management
- **Certificate Operations**:
  - Self-signed CA generation (`netcrave pki_init_ca`)
  - Certificate issuance with templates (`netcrave pki_issue_cert`)
  - Certificate revocation (`netcrave pki_revoke_cert`)
  - CRL generation (`netcrave pki_generate_crl`)
  - Certificate listing from LDAP (`netcrave pki_list_certs`)

### Email Security
- **OpenDKIM** - DKIM selector and key container for email signing

### Network Services
- **ICAP Server Integration** - Squid proxy content adaptation server
  - Request/Response modification support
  - Kerberos authentication for access control
  - Celery async processing
- **Sendmail/Postfix** - Mail routing and alias management

## Installation

```bash
# Install in editable mode for development
poetry install

# Or build and install
poetry build
pip install dist/django-ldap-0.1.0-py3-none-any.whl
```

### Dependencies
- Python 3.9+
- Django 4.2+
- python-ldap - LDAP directory integration
- pyasn1 - ASN.1/DER encoding for PKI
- cryptography - Certificate generation and verification
- celery - Async task processing (ICAP, email notifications)

## Configuration

### Environment Variables

| Setting | Default | Description |
|---------|---------|-------------|
| `LDAP_BASE_DN` | dc=example,dc=com | Base DN for LDAP directory |
| `DJANGO_SECRET_KEY` | Auto-generated | Django secret key |
| `DJANGO_DEBUG` | false | Debug mode (set to true for development) |

### LDAP Subtree Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `LDAP_OU_USERS` | ou=users | Users container |
| `LDAP_OU_GROUPS` | ou=groups | Groups container |
| `LDAP_OU_COMPUTERS` | ou=computers | Computers container |
| `LDAP_OU_DNS` | ou=dns | DNS zones container |
| `LDAP_OU_AST` | ou=asterisk | Asterisk configuration |
| `LDAP_OU_RADIUS` | ou=radius | RADIUS clients/container |
| `LDAP_OU_KRB` | ou=kerberos | Kerberos realm container |
| `LDAP_OU_ICAP` | ou=icap | ICAP service configuration |
| `LDAP_OU_DKIM` | ou=dkim | OpenDKIM configuration |
| `LDAP_OU_CERTIFICATES` | ou=certificates | PKI/Certificate storage OU |

### Auto-Increment Counters

| Setting | Default | Description |
|---------|---------|-------------|
| `LDAP_DEFAULT_UID_NUMBER` | 1000 | Starting UID for new users |
| `LDAP_DEFAULT_GID_NUMBER` | 100 | Starting GID for new groups |

### POSIX Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `LDAP_DEFAULT_LOGIN_SHELL` | /bin/bash | User login shell |
| `LDAP_DEFAULT_HOME_BASE` | /home | Home directory base path |
| `LDAP_DEFAULT_GECOS` | System User | User full name/default |

### DNS Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `LDAP_DEFAULT_DNS_TTL` | 3600 | Default DNS record TTL |
| `LDAP_DEFAULT_SOA_SERIAL` | %Y%m%d01 | Date-based SOA serial format |

### Asterisk Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `ASTERISK_DEFAULT_CONTEXT` | default | Dialplan context |
| `ASTERISK_DEFAULT_TRANSPORT` | udp | SIP transport protocol |

### RADIUS Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `RADIUS_DEFAULT_AUTH_TYPE` | PAP | Authentication type |
| `RADIUS_DEFAULT_SESSION_TIMEOUT` | 3600 | Session timeout (seconds) |

### Kerberos Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `KRB_DEFAULT_MAX_PWD_LIFE` | 7776000 | Max password age (90 days) |
| `KRB_DEFAULT_TICKET_LIFETIME` | 86400 | Ticket lifetime (24 hours) |

### PKI / Certificate Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `LDAP_OU_ACME` | ou=acme | ACME certificate storage OU |
| `ACME_BASE_URL` | /ca/acme/ | ACME API endpoint base URL |

### ICAP Server Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `ICAP_SERVER_HOST` | 127.0.0.1 | ICAP server bind address |
| `ICAP_SERVER_PORT` | 1344 | ICAP server port (standard) |
| `LDAP_OU_ICAP_USERS` | ou=icap-users | ICAP user access OU |

### Celery Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `CELERY_BROKER_URL` | redis://localhost:6379/0 | Redis broker URL |
| `CELERY_RESULT_BACKEND` | redis://localhost:6379/1 | Redis result backend |

## Command Line Interface

Use the `netcrave` command instead of Django's `manage.py`:

```bash
# Initialize the LDAP directory tree structure
netcrave init_tree

# Show directory information and entry counts
netcrave ldap_info --counts

# Backup LDAP directory to LDIF or JSON format
netcrave backup_ldap /path/to/backup.ldif
netcrave backup_ldap /path/to/backup.json --format=json

# Create a superuser for admin access
netcrave createsuperuser

# Run the development server
netcrave runserver

# Start ICAP Celery worker
netcrave start_icap
```

### Management Commands

| Command | Description |
|---------|-------------|
| `init_tree` | Initialize base LDAP structure (OUs, counters, default policies) |
| `delete_tree <dn>` | Safely delete LDAP entries with dependency checks |
| `backup_ldap` | Backup LDAP database to LDIF or JSON format |
| `ldap_info` | Display LDAP tree structure, entry counts, schema info |
| `start_icap` | Start Celery worker for ICAP processing |

### PKI Management Commands

| Command | Description |
|---------|-------------|
| `pki_init_ca` | Initialize a new self-signed CA certificate |
| `pki_issue_cert` | Issue a certificate signed by the CA using a template |
| `pki_revoke_cert` | Revoke a certificate in the Certificate Authority |
| `pki_list_certs` | List certificates stored in LDAP directory |
| `pki_generate_crl` | Generate a Certificate Revocation List (CRL) |
| `pki_create_default_profile` | Create default certificate profile for ACME |

## Admin Interface

Access the Django admin at `/admin/`:

### Users & Groups
- **Users**: Full user management with POSIX, Kerberos, RADIUS attributes
- **Groups**: POSIX groups and groupOfNames with member management

### Networking
- **DNS**: Zone management (PDNSDomain) and record management (PDNSRecord)
- **Computers**: Device registration with IP/MAC tracking

### Telephony
- **Asterisk**: SIP/IAX endpoints, voicemail, dialplan configuration

### Authentication & Security
- **RADIUS**: Client registration and user RADIUS profiles
- **Kerberos**: Realm configuration, principals, password/ticket policies
- **PKI/Certificate Authority**:
  - Certificate templates for reusable certificate configurations
  - Certificate profiles mapping hostnames to templates for ACME
  - Certificate records stored in LDAP (valid/revoked/expired)
  - Kerberos authentication required for ACME operations (network-admins only)
  - OCSP responder for certificate status

### Network Services
- **ICAP Server**: Service configuration, user access control

## Project Structure

```
netcrave/
├── __init__.py          # Main project package
├── cli.py               # Main entry point for 'netcrave' command
├── asgi.py              # ASGI application (replaces WSGI)
├── urls.py              # Root URL configuration
└── settings.py          # Django settings with LDAP configuration

netcrave_config/         # Configuration package
├── settings.py          # Shared Django settings
├── management/
│   └── commands/
│       └── create_defaults.py  # Default data creation

netcrave_ldap/           # Core LDAP models app
├── models/              # User, Group, Computer, PowerDNS, Asterisk, RADIUS, Kerberos
├── admin/               # Admin interface for each model type
├── utils/               # Utility functions (DN building, defaults)
├── management/commands/
│   ├── init_tree.py     # Initialize LDAP directory tree
│   ├── delete_tree.py   # Delete LDAP entries safely
│   ├── backup_ldap.py   # Backup LDAP to LDIF/JSON
│   └── ldap_info.py     # Show directory information

netcrave_ca/             # Certificate Authority app
├── models.py            # LDAP-backed certificate templates/profiles/records
├── utils/
│   └── acme.py          # ACME protocol utilities with Kerberos auth
├── views/
│   ├── ocsp.py          # OCSP responder
│   └── acme.py          # ACME protocol endpoints with Kerberos auth
└── management/commands/

netcrave_icap/           # ICAP server integration
├── models.py            # LDAP-backed ICAP service and user profiles
├── admin.py             # Admin interface
├── tasks.py             # Celery async processing tasks
├── views.py             # HTTP/ICAP bridge views
└── management/commands/
    └── start_icap.py    # Start Celery worker

schemas/                 # LDAP schema files
├── openldap/            # Core OpenLDAP schemas
├── krb5/                # Kerberos schema
├── freeradius/          # RADIUS schema
├── asterisk/            # Asterisk schema
├── powerdns/            # PowerDNS schema
├── sendmail/            # Sendmail schema
└── netcrave/            # Netcrave custom schemas (ICAP, Certificate)

3rdparty/python-ldap/    # vendored python-ldap library
```

## Schema Compliance

All models conform to the LDAP schemas in `schemas/`:

| Schema | Purpose |
|--------|---------|
| openldap/core.schema | Basic object classes (top, device) |
| openldap/inetorgperson.schema | User information (inetOrgPerson) |
| openldap/nis.schema | POSIX accounts and groups |
| openldap/misc.schema | Additional LDAP utilities |
| krb5/kerberos.schema | Kerberos identity management |
| freeradius/freeradius.schema | RADIUS authentication |
| asterisk/asterisk.schema | Asterisk telephony configuration |
| powerdns/dnsdomain2.schema | PowerDNS DNS zone management |
| sendmail/sendmail.schema | Sendmail MTA configuration |
| netcrave/netcrave-icap.schema | ICAP service configuration |
| netcrave/netcrave-certificate.schema | Certificate templates, profiles, and records |

## ACME Protocol Support

The PKI/Certificate Authority includes full ACME (RFC 8555) protocol support:

- **Directory endpoint**: `/ca/acme/directory`
- **New nonce**: `/ca/acme/new-nonce`
- **Account management**: `/ca/acme/new-account`
- **Order management**: `/ca/acme/new-order`
- **Challenge validation**: `/ca/acme/challenge/<id>`
- **Certificate issuance**: `/ca/acme/issue-cert`

Access is restricted to network administrators via Kerberos authentication.

## OCSP Responder

Online Certificate Status Protocol (RFC 6960) responder for certificate status checking:

- **OCSP endpoint**: `POST /ca/ocsp/` - Accepts DER-encoded OCSP requests
- **Status endpoint**: `GET /ca/ocsp/status/` - Service health check

## ICAP Server Integration

The ICAP server integrates with Squid proxy for content adaptation:

1. Squid sends ICAP requests to the configured ICAP server
2. The view bridges HTTP/ICAP protocols via custom headers
3. Kerberos authentication validates user identity against LDAP
4. Celery processes requests asynchronously
5. Logs are sent to syslog (not stored in database)

## License

MIT License - See LICENSE file for details.
