# Django LDAP Management

Django application for managing LDAP infrastructure including:

- **Users** (inetOrgPerson + posixAccount + kerberos + radius)
- **Groups** (posixGroup, groupOfNames)
- **Computers** (device + ipHost)
- **PowerDNS** (dNSDomain2 + PdnsDomain/PdnsRecord)
- **Asterisk** (extensions, IAX/SIP endpoints, voicemail)
- **RADIUS** (radiusprofile aux, radiusClient)
- **Kerberos** (krbRealmContainer, krbPrincipal, policies)
- **Sendmail/Postfix** (MTA servers, maps/aliases)

## Installation

```bash
# Install in editable mode for development
pip install -e .

# Or build and install
pip build .
pip install ldap_management-0.1.0-py3-none-any.whl
```

## Configuration

Set environment variables or use defaults:

| Setting | Default |
|---------|---------|
| `LDAP_BASE_DN` | dc=example,dc=com |
| `DJANGO_SECRET_KEY` | Auto-generated dev key |
| `DJANGO_DEBUG` | true |

## Command Line Interface

After installation, use `dldap` instead of `manage.py`:

```bash
# Initialize the LDAP tree structure
dldap init_tree

# Show directory information
dldap ldap_info --counts

# Backup LDAP directory
dldap backup_ldap /path/to/backup.json

# Create a superuser for admin access
dldap createsuperuser

# Run the development server
dldap runserver
```

## Admin Interface

Access the Django admin at `/admin/`:

- **Users**: Full user management with POSIX, Kerberos, RADIUS attributes
- **Groups**: POSIX groups and groupOfNames with member management
- **DNS**: Zone management (PDNSDomain) and record management (PDNSRecord)
- **Asterisk**: SIP/IAX endpoints, voicemail, dialplan configuration
- **Kerberos**: Realm configuration, principals, password/ticket policies

## Project Structure

```
ldap_admin/
├── models/          # All LDAP-backed Django models
├── admin/           # Admin interface for each model type
├── management/      # Custom Django management commands
├── utils/           # Utility functions (DN building, defaults, crypto)
└── migrations/      # Database migrations
```

## Schema Compliance

All models conform to the LDAP schemas in `schemas/`:
- openldap/core.schema
- openldap/inetorgperson.schema  
- openldap/nis.schema
- krb5/kerberos.schema
- freeradius/freeradius.schema
- asterisk/asterisk.schema
- powerdns/dnsdomain2.schema
- sendmail/sendmail.schema
