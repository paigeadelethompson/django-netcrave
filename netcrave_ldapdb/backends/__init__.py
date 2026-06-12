"""
Netcrave LDAP Database Backend for Django.

This package provides a Django database backend that uses OpenLDAP as the backing store.
It implements Django's database API to work with LDAP directories.

Usage:
    DATABASES = {
        'default': {
            'ENGINE': 'netcrave_ldapdb.backends',
            'LDAP_SERVER_URI': 'ldap://localhost:389',
            'LDAP_BASE_DN': 'dc=example,dc=com',
            'LDAP_BIND_DN': 'cn=admin,dc=example,dc=com',
            'LDAP_BIND_PASSWORD': 'secret',
        }
    }

Features:
- Maps Django models to LDAP entries
- Handles auto-increment counters via LDAP counter entries
- Supports relationships via DN references
- Type conversion between Django fields and LDAP attributes
"""

# Import the database wrapper for registration
from .database_wrapper import DatabaseWrapper
