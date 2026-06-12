"""
Netcrave LDAP Database Backend for Django.

Usage:
    DATABASES = {
        'default': {
            'ENGINE': 'netcrave_ldapdb.backends',
            'LDAP_SERVER_URI': 'ldap://localhost:389',
            'LDAP_BASE_DN': 'dc=example,dc=com',
        }
    }
"""

from netcrave_ldapdb.backends.base import (
    DatabaseWrapper,
    get_ldap_connection,
)

__all__ = ['DatabaseWrapper', 'get_ldap_connection']
