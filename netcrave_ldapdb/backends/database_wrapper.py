"""
Database Wrapper module for netcrave_ldapdb backend.

This is the main entry point that Django uses to connect to LDAP.
"""

import logging

from django.conf import settings
from django.db.backends.base.base import BaseDatabaseWrapper

from .operations import DatabaseOperations
from .features import DatabaseFeatures
from .introspection import LDAPIntrospection
from .schema import LDAPSchemaEditor
from .base import Cursor, get_ldap_connection

logger = logging.getLogger(__name__)


class DatabaseWrapper(BaseDatabaseWrapper):
    """Django database wrapper for OpenLDAP."""

    vendor = 'netcrave_ldap'
    display_name = 'Netcrave LDAP'

    # Backend modules
    SchemaEditorClass = LDAPSchemaEditor
    operations_class = DatabaseOperations
    features_class = DatabaseFeatures
    introspection_class = LDAPIntrospection

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configure the backend-specific settings
        self.server_uri = self.settings_dict.get(
            'LDAP_SERVER_URI', getattr(settings, 'LDAP_SERVER_URI', 'ldap://localhost')
        )
        self.base_dn = self.settings_dict.get(
            'BASE_DN', getattr(settings, 'LDAP_BASE_DN', 'dc=example,dc=com')
        )
        self.bind_dn = self.settings_dict.get(
            'BIND_DN', getattr(settings, 'LDAP_BIND_DN', None)
        )
        self.bind_password = self.settings_dict.get(
            'BIND_PASSWORD', getattr(settings, 'LDAP_BIND_PASSWORD', None)
        )

    def get_connection_params(self):
        """Get parameters for connecting to LDAP."""
        return {
            'server_uri': self.server_uri,
            'base_dn': self.base_dn,
            'bind_dn': self.bind_dn,
            'bind_password': self.bind_password,
        }

    def get_new_connection(self, params):
        """Create a new connection to LDAP."""
        # The connection is managed by the ldap_backend module
        conn = get_ldap_connection()
        return conn

    def init_connection_state(self):
        """Initialize the connection state."""
        pass  # Connection is lazy-loaded

    def create_cursor(self, name=None):
        """Create a new cursor for executing queries."""
        return Cursor(self)

    def _set_autocommit(self, autocommit):
        """Set autocommit mode (LDAP has no transactions)."""
        pass

    def check_constraints(self, table_names=None):
        """Check foreign key constraints."""
        pass  # LDAP doesn't have FK constraints

    def close(self):
        """Close the connection."""
        try:
            get_ldap_connection().disconnect()
        except Exception:
            pass

    def is_usable(self):
        """Check if the connection is still usable."""
        try:
            conn = get_ldap_connection()
            # Try a simple search
            conn.search(self.base_dn, filterstr="(objectClass=*)", scope=0)
            return True
        except Exception:
            return False

    def quote_name(self, name):
        """Quote a database name for use in SQL."""
        # LDAP doesn't need quoting like SQL, but we keep it consistent
        if not name.startswith('"') and not name.endswith('"'):
            name = f'"{name}"'
        return name

    def validate_autocommit(self):
        """Validate that autocommit is enabled (LDAP has no transactions)."""
        pass

    def set_rollback(self):
        """Set the rollback flag."""
        # LDAP has no transactions to rollback
        pass

    def in_atomic_block(self):
        """Check if we're in an atomic block."""
        return False  # LDAP has no transactions
