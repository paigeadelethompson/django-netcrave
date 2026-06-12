"""Introspection module for netcrave_ldapdb backend."""

from typing import Any, Dict, List

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
        return [
            'ldap_users',
            'ldap_posix_groups',
            'ldap_computers',
            'ldap_dns_zones',
            'ldap_asterisk',
            'ldap_radius',
            'ldap_kerberos',
        ]

    def get_table_description(self, cursor, table_name: str) -> List[LDAPFieldInfo]:
        """Get description of an LDAP 'table' (OU structure)."""
        return []

    def get_relations(self, cursor, table_name: str) -> Dict:
        """Get relationships between LDAP entries."""
        relations = {}
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
    """
    from netcrave_ldapdb.backends import get_ldap_connection

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
    """
    schema = {
        'top': {'type': 'ABSTRACT', 'must': [], 'may': ['objectClass', 'description']},
        'person': {'type': 'STRUCTURAL', 'must': ['sn', 'cn'], 'may': ['userPassword', 'telephoneNumber']},
        'inetOrgPerson': {'type': 'STRUCTURAL', 'must': ['sn', 'cn'], 'may': ['userPassword', 'uid', 'mail']},
        'posixAccount': {'type': 'AUXILIARY', 'must': ['cn', 'uid', 'uidNumber', 'gidNumber', 'homeDirectory']},
        'posixGroup': {'type': 'STRUCTURAL', 'must': ['cn', 'gidNumber'], 'may': ['userPassword', 'memberUid']},
        'groupOfNames': {'type': 'STRUCTURAL', 'must': ['cn', 'member'], 'may': ['description', 'userPassword']},
    }
    return schema
