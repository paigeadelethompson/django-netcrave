"""
Introspection module for netcrave_ldapdb backend.

This provides database introspection capabilities for LDAP directories.
"""

from typing import Any, Dict, List, Optional

import ldap
from django.conf import settings
from django.db.backends.base.introspection import BaseDatabaseIntrospection


class LDAPFieldInfo:
    """Information about an LDAP field/attribute."""

    def __init__(self,
                 name: str,
                 type_code: str,
                 null_ok: bool = True,
                 default: Any = None):
        self.name = name
        self.type_code = type_code
        self.null_ok = null_ok
        self.default = default


class LDAPIntrospection(BaseDatabaseIntrospection):
    """LDAP directory introspection."""

    data_types_reverse = {
        'INTEGER': 'PositiveIntegerField',
        'IA5String': 'CharField',
        'LDAPString': 'CharField',
        'DirectoryString': 'CharField',
        'Boolean': 'BooleanField',
        'GeneralizedTime': 'DateTimeField',
        'CertificateList': 'TextField',
        'Certificate': 'TextField',
    }

    def get_table_list(self, cursor) -> List[str]:
        """Get list of LDAP OUs that can be treated as tables."""
        # Return common OU names that are typically used
        return [
            'ldap_users',       # ou=users
            'ldap_posix_groups',  # ou=groups
            'ldap_computers',   # ou=computers
            'ldap_dns_zones',   # ou=dns
            'ldap_asterisk',    # ou=asterisk
            'ldap_radius',      # ou=radius
            'ldap_kerberos',    # ou=kerberos
        ]

    def get_table_description(self, cursor, table_name: str) -> List[LDAPFieldInfo]:
        """Get description of an LDAP 'table' (OU structure)."""
        return []

    def get_relations(self, cursor, table_name: str) -> Dict:
        """Get relationships between LDAP entries."""
        relations = {}
        # For LDAP, relationships are via DN references
        return relations

    def get_indexes(self, cursor, table_name: str) -> Dict:
        """Get index information (LDAP doesn't have indexes like SQL)."""
        return {}

    def get_constraints(self, cursor, table_name: str) -> Dict:
        """Get constraint information."""
        return {}


def introspect_ldap_tree(base_dn: str = None, depth: int = 2) -> Dict[str, Any]:
    """
    Introspect the LDAP directory structure.

    Args:
        base_dn: Starting DN for introspection
        depth: How deep to traverse

    Returns:
        Dictionary mapping DNs to their attributes
    """
    from netcrave_ldap.utils.ldap_backend import get_ldap_connection

    if base_dn is None:
        base_dn = getattr(settings, 'LDAP_BASE_DN', 'dc=example,dc=com')

    conn = get_ldap_connection()
    results = conn.search(
        base_dn=base_dn,
        scope=ldap.SCOPE_SUBTREE,
        filterstr="(objectClass=*)",
        attrs=['objectClass', 'cn', 'ou', 'description']
    )

    tree = {}
    for dn, attrs in results:
        tree[dn] = {
            'attributes': attrs,
            'object_classes': attrs.get('objectClass', []),
        }

    return tree


def get_ldap_schema() -> Dict[str, Dict]:
    """
    Get the LDAP schema information.

    Returns:
        Dictionary of object class definitions
    """
    # Common OpenLDAP object classes we support
    schema = {
        'top': {
            'type': 'ABSTRACT',
            'must': [],
            'may': ['objectClass', 'description'],
        },
        'person': {
            'type': 'STRUCTURAL',
            'must': ['sn', 'cn'],
            'may': ['userPassword', 'telephoneNumber', 'facsimileTelephoneNumber', 'internationalISDNNumber',
                    'telexNumber', 'teletexTerminalIdentifier', 'street', 'postOfficeBox', 'postalCode',
                    'physicalDeliveryOfficeName', 'title', 'st', 'l', 'o', 'ou', 'dc', 'description'],
        },
        'inetOrgPerson': {
            'type': 'STRUCTURAL',
            'must': ['sn', 'cn'],
            'may': ['userPassword', 'telephoneNumber', 'facsimileTelephoneNumber', 'internationalISDNNumber',
                    'telexNumber', 'teletexTerminalIdentifier', 'street', 'postOfficeBox', 'postalCode',
                    'physicalDeliveryOfficeName', 'title', 'st', 'l', 'o', 'ou', 'dc', 'description',
                    'initials', 'employeeNumber', 'employeeType', 'givenName', 'displayName',
                    'preferredLanguage', 'uid'],
        },
        'posixAccount': {
            'type': 'AUXILIARY',
            'must': ['cn', 'uid', 'uidNumber', 'gidNumber', 'homeDirectory'],
            'may': ['userPassword', 'loginShell', 'gecos', 'shadowLastChange', 'shadowMin',
                    'shadowMax', 'shadowWarning', 'shadowInactive', 'shadowExpire', 'shadowFlag',
                    'description', 'entryTimestamp'],
        },
        'posixGroup': {
            'type': 'STRUCTURAL',
            'must': ['cn', 'gidNumber'],
            'may': ['userPassword', 'memberUid', 'description', 'entryTimestamp'],
        },
        'groupOfNames': {
            'type': 'STRUCTURAL',
            'must': ['cn', 'member'],
            'may': ['businessCategory', 'seeAlso', 'owner', 'ou', 'o', 'description', 'userPassword'],
        },
        'krbPrincipal': {
            'type': 'STRUCTURAL',
            'must': ['krbPrincipalName'],
            'may': ['krbCanonicalName', 'krbPrincipalType', 'krbUpEnabled', 'krbPrincipalExpiration',
                    'krbPasswordExpiration', 'krbLastSuccessfulAuth', 'krbLastFailedAuth',
                    'krbLoginFailedCount', 'krbTicketPolicyReference', 'krbPwdPolicyReference',
                    'krbTicketFlags', 'krbMaxTicketLife', 'krbMaxRenewableAge',
                    'krbAllowedToDelegateTo', 'krbPrincipalAuthInd'],
        },
    }
    return schema
