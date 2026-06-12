"""
Custom LDAP backend for Django using python-ldap.

This module provides:
- LDAPConnection: Direct connection to OpenLDAP server
- get_ldap_connection(): Factory function for singleton connection

Example usage:
    from netcrave_ldap.ldap_backend import get_ldap_connection

    conn = get_ldap_connection()
    result = conn.search("ou=users,dc=example,dc=com", filterstr="(uid=admin)")
"""

import ldap
import ldap.modlist
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class LDAPConnection:
    """Direct LDAP connection using python-ldap.

    Provides CRUD operations on LDAP entries:
    - search: Query LDAP directory
    - get: Retrieve single entry by DN
    - add: Create new entries
    - modify: Update existing entries
    - delete: Remove entries

    Connection is lazy-loaded and reused across calls.
    """

    def __init__(self, server_uri: str = None, base_dn: str = None):
        self.server_uri = server_uri or getattr(settings, 'LDAP_SERVER_URI', 'ldap://localhost')
        self.base_dn = base_dn or getattr(settings, 'LDAP_BASE_DN', 'dc=example,dc=com')
        self.bind_dn = getattr(settings, 'LDAP_BIND_DN', None)
        self.bind_password = getattr(settings, 'LDAP_BIND_PASSWORD', None)
        self.conn = None

    def connect(self):
        """Establish connection to LDAP server."""
        if self.conn:
            return self.conn

        try:
            # Create LDAP object
            self.conn = ldap.initialize(self.server_uri)

            # Set options for better compatibility
            self.conn.set_option(ldap.OPT_REFERRALS, 0)
            self.conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            self.conn.set_option(ldap.OPT_TIMEOUT, 10)

            # Bind if credentials provided, otherwise anonymous bind
            if self.bind_dn and self.bind_password:
                self.conn.simple_bind_s(self.bind_dn, self.bind_password)
            else:
                self.conn.simple_bind_s()

            logger.debug(f"Connected to LDAP server: {self.server_uri}")
            return self.conn

        except ldap.LDAPError as e:
            logger.error(f"LDAP connection failed: {e}")
            raise

    def disconnect(self):
        """Close the LDAP connection."""
        if self.conn:
            try:
                self.conn.unbind_s()
            except ldap.LDAPError:
                pass
            finally:
                self.conn = None

    def search(
        self,
        base_dn: str,
        scope: int = ldap.SCOPE_SUBTREE,
        filterstr: str = "(objectClass=*)",
        attrs: List[str] = None,
    ) -> List[Tuple[str, Dict]]:
        """Perform an LDAP search.

        Args:
            base_dn: Base DN to search from
            scope: Search scope (SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE)
            filterstr: LDAP search filter
            attrs: List of attributes to return (None for all)

        Returns:
            List of (dn, attributes) tuples
        """
        if not self.conn:
            self.connect()

        try:
            result = self.conn.search_s(base_dn, scope, filterstr, attrs or [])
            logger.debug(f"Search returned {len(result)} entries")
            return result
        except ldap.LDAPError as e:
            logger.error(f"LDAP search failed: {e}")
            raise

    def get(self, dn: str, attrs: List[str] = None) -> Optional[Tuple[str, Dict]]:
        """Get a single entry by DN.

        Args:
            dn: Distinguished name of the entry
            attrs: List of attributes to return (None for all)

        Returns:
            (dn, attributes) tuple or None if not found
        """
        try:
            result = self.search(dn, ldap.SCOPE_BASE, "(objectClass=*)", attrs)
            return result[0] if result else None
        except ldap.NO_SUCH_OBJECT:
            return None

    def add(self, dn: str, attributes: Dict[str, Any]) -> bool:
        """Add a new LDAP entry.

        Args:
            dn: Distinguished name for the new entry
            attributes: Dictionary of attribute values

        Returns:
            True if successful, False if already exists
        """
        if not self.conn:
            self.connect()

        try:
            # Build modlist from attributes
            modlist = ldap.modlist.addModlist(attributes)

            # Add the entry
            self.conn.add_s(dn, modlist)
            logger.debug(f"Added entry: {dn}")
            return True
        except ldap.ALREADY_EXISTS:
            logger.warning(f"Entry already exists: {dn}")
            return False
        except ldap.LDAPError as e:
            logger.error(f"Failed to add entry {dn}: {e}")
            raise

    def modify(self, dn: str, changes: Dict[str, List[Tuple[int, Any]]]) -> bool:
        """Modify an existing LDAP entry.

        Args:
            dn: Distinguished name of the entry
            changes: Dictionary mapping attribute names to lists of (mod_op, value) tuples
                mod_op: ldap.MOD_ADD, ldap.MOD_REPLACE, ldap.MOD_DELETE

        Returns:
            True if successful
        """
        if not self.conn:
            self.connect()

        try:
            # Build modlist from changes
            modlist = []
            for attr, change_list in changes.items():
                for mod_op, value in change_list:
                    modlist.append((mod_op, attr, value))

            # Modify the entry
            self.conn.modify_s(dn, modlist)
            logger.debug(f"Modified entry: {dn}")
            return True
        except ldap.LDAPError as e:
            logger.error(f"Failed to modify entry {dn}: {e}")
            raise

    def delete(self, dn: str) -> bool:
        """Delete an LDAP entry.

        Args:
            dn: Distinguished name of the entry

        Returns:
            True if successful
        """
        if not self.conn:
            self.connect()

        try:
            # First check if entry exists and has children
            try:
                result = self.search(dn, ldap.SCOPE_BASE, "(objectClass=*)")
                if not result:
                    logger.warning(f"Entry does not exist: {dn}")
                    return False
            except ldap.NO_SUCH_OBJECT:
                return False

            # Delete the entry
            self.conn.delete_s(dn)
            logger.debug(f"Deleted entry: {dn}")
            return True
        except ldap.LDAPError as e:
            logger.error(f"Failed to delete entry {dn}: {e}")
            raise

    def search_paginated(
        self,
        base_dn: str,
        scope: int = ldap.SCOPE_SUBTREE,
        filterstr: str = "(objectClass=*)",
        attrs: List[str] = None,
        page_size: int = 100,
    ) -> List[Tuple[str, Dict]]:
        """Perform a paged LDAP search for large result sets.

        Args:
            base_dn: Base DN to search from
            scope: Search scope
            filterstr: LDAP search filter
            attrs: List of attributes to return
            page_size: Number of entries per page

        Returns:
            List of (dn, attributes) tuples
        """
        if not self.conn:
            self.connect()

        results = []
        cookie = ''

        while True:
            try:
                msg_id = self.conn.search_ext(
                    base_dn,
                    scope,
                    filterstr,
                    attrs or [],
                    serverctrls=[ldap.controls.SimplePagedResultsControl(True, page_size, cookie)],
                )
                rtype, rdata, rmsg_id, resp_ctrls = self.conn.result3(msg_id)

                results.extend(rdata)

                # Check for more pages
                pctrls = [
                    c
                    for c in resp_ctrls
                    if c.controlType == ldap.controls.SimplePagedResultsControl.controlType
                ]
                if pctrls and pctrls[0].cookie:
                    cookie = pctrls[0].cookie
                else:
                    break

            except ldap.LDAPError as e:
                logger.error(f"Paged search failed: {e}")
                raise

        return results


def get_ldap_connection() -> LDAPConnection:
    """Get or create a global singleton LDAP connection.

    Returns:
        LDAPConnection instance
    """
    if not hasattr(LDAPConnection, '_instance'):
        LDAPConnection._instance = LDAPConnection()
    return LDAPConnection._instance
