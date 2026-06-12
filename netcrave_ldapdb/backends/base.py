"""
Django LDAP Database Backend - Base module.

This provides a Django database backend that uses OpenLDAP as the backing store.
It implements Django's database API to work with LDAP directories.

Key features:
- Maps Django models to LDAP entries
- Handles auto-increment counters via LDAP counter entries
- Supports relationships via DN references
- Type conversion between Django fields and LDAP attributes
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import ldap
from django.conf import settings
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.utils import CursorWrapper

logger = logging.getLogger(__name__)

# Import the LDAP connection module (from netcrave/utils)
try:
    from django.conf import settings
    import ldap

    class LDAPConnection:
        """Simplified LDAP connection wrapper for backend use."""

        def __init__(self):
            self.server_uri = getattr(settings, 'LDAP_SERVER_URI', 'ldap://localhost')
            self.base_dn = getattr(settings, 'LDAP_BASE_DN', 'dc=example,dc=com')
            self.bind_dn = getattr(settings, 'LDAP_BIND_DN', None)
            self.bind_password = getattr(settings, 'LDAP_BIND_PASSWORD', None)
            self.conn = None

        def connect(self):
            """Establish connection to LDAP server."""
            if self.conn:
                return self.conn
            self.conn = ldap.initialize(self.server_uri)
            self.conn.set_option(ldap.OPT_REFERRALS, 0)
            self.conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            self.conn.set_option(ldap.OPT_TIMEOUT, 10)
            if self.bind_dn and self.bind_password:
                self.conn.simple_bind_s(self.bind_dn, self.bind_password)
            else:
                self.conn.simple_bind_s()
            return self.conn

        def search(self, base_dn: str, scope: int = ldap.SCOPE_SUBTREE,
                   filterstr: str = "(objectClass=*)",
                   attrs: List[str] = None) -> List[Tuple[str, Dict]]:
            """Perform an LDAP search."""
            if not self.conn:
                self.connect()
            return self.conn.search_s(base_dn, scope, filterstr, attrs or [])

        def get(self, dn: str, attrs: List[str] = None):
            """Get a single entry by DN."""
            try:
                result = self.search(dn, ldap.SCOPE_BASE, "(objectClass=*)", attrs)
                return result[0] if result else None
            except ldap.NO_SUCH_OBJECT:
                return None

        def add(self, dn: str, attributes: Dict) -> bool:
            """Add a new LDAP entry."""
            if not self.conn:
                self.connect()
            try:
                import ldap.modlist
                modlist = ldap.modlist.addModlist(attributes)
                self.conn.add_s(dn, modlist)
                return True
            except ldap.ALREADY_EXISTS:
                return False

        def modify(self, dn: str, changes: Dict) -> bool:
            """Modify an existing LDAP entry."""
            if not self.conn:
                self.connect()
            try:
                modlist = []
                for attr, change_list in changes.items():
                    for mod_op, value in change_list:
                        modlist.append((mod_op, attr, value))
                self.conn.modify_s(dn, modlist)
                return True
            except ldap.LDAPError as e:
                raise

        def delete(self, dn: str) -> bool:
            """Delete an LDAP entry."""
            if not self.conn:
                self.connect()
            try:
                self.conn.delete_s(dn)
                return True
            except ldap.LDAPError as e:
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
except ImportError:
    # Fallback - define minimal connection class
    class LDAPConnection:
        def __init__(self):
            pass

        def connect(self):
            raise NotImplementedError("python-ldap not available")

        def search(self, base_dn: str, scope: int = ldap.SCOPE_SUBTREE,
                   filterstr: str = "(objectClass=*)",
                   attrs: List[str] = None) -> List[Tuple[str, Dict]]:
            raise NotImplementedError

        def get(self, dn: str, attrs: List[str] = None):
            raise NotImplementedError

        def add(self, dn: str, attributes: Dict) -> bool:
            raise NotImplementedError

        def modify(self, dn: str, changes: Dict) -> bool:
            raise NotImplementedError

        def delete(self, dn: str) -> bool:
            raise NotImplementedError


def get_ldap_connection() -> LDAPConnection:
    """Get or create the global LDAP connection."""
    return get_ldap_connection()


class Cursor(CursorWrapper):
    """LDAP cursor that implements Django's database cursor interface."""

    def __init__(self, connection):
        super().__init__(connection)
        self.connection = connection

    def execute(self, sql: str, params: Optional[List] = None) -> None:
        """Execute an SQL-like query against LDAP."""
        logger.debug(f"Executing: {sql} with params: {params}")

        # Parse the SQL to determine operation type
        sql_upper = sql.strip().upper()

        if sql_upper.startswith('SELECT'):
            self.result_set = self._execute_select(sql, params)
        elif sql_upper.startswith('INSERT'):
            self.result_set = self._execute_insert(sql, params)
        elif sql_upper.startswith('UPDATE'):
            self.result_set = self._execute_update(sql, params)
        elif sql_upper.startswith('DELETE'):
            self.result_set = self._execute_delete(sql, params)
        else:
            raise NotImplementedError(f"Unsupported SQL: {sql}")

    def _execute_select(self, sql: str, params: Optional[List]) -> List[Dict]:
        """Execute SELECT query against LDAP."""
        # Parse basic WHERE clause
        where_clause = ""
        if "WHERE" in sql.upper():
            parts = sql.upper().split("WHERE", 1)
            where_clause = parts[1].strip()

        # Extract table name (simplified - assumes FROM table_name)
        from_match = sql.upper().find("FROM")
        if from_match > 0:
            rest = sql[from_match + 4:].strip()
            table_name = rest.split()[0] if rest else ""
        else:
            table_name = ""

        # Convert table name to base DN
        base_dn = self._table_to_dn(table_name)

        # Build LDAP filter from WHERE clause
        ldap_filter = "(objectClass=*)"
        if where_clause:
            ldap_filter = self._where_to_filter(where_clause)

        # Execute search
        results = get_ldap_connection().search(
            base_dn=base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=ldap_filter,
            attrs=['*', '+']
        )

        return self._format_results(results)

    def _execute_insert(self, sql: str, params: Optional[List]) -> int:
        """Execute INSERT query - creates LDAP entry."""
        # Parse INSERT INTO table (cols) VALUES (vals)
        import re

        match = re.match(
            r"INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)",
            sql, re.IGNORECASE
        )
        if not match:
            raise NotImplementedError(f"Cannot parse INSERT: {sql}")

        table_name = match.group(1)
        columns = [c.strip() for c in match.group(2).split(',')]
        values = [self._parse_value(v.strip()) for v in match.group(3).split(',')]

        # Build entry attributes
        attrs = {}
        for col, val in zip(columns, values):
            ldap_attr = self._column_to_ldap_attr(table_name, col)
            if isinstance(val, list):
                attrs[ldap_attr] = val
            else:
                attrs[ldap_attr] = [val]

        # Get DN from table and primary key
        cn_value = attrs.get('cn', [None])[0]
        uid_value = attrs.get('uid', [None])[0]
        base_dn = self._table_to_dn(table_name)

        if cn_value:
            dn = f"cn={self._escape_rdn(cn_value)},{base_dn}"
        elif uid_value:
            dn = f"uid={self._escape_rdn(uid_value)},{base_dn}"
        else:
            raise ValueError("Cannot determine DN - missing cn or uid")

        # Add objectClass if not present
        if 'objectClass' not in attrs:
            attrs['objectClass'] = ['top']

        # Create entry
        get_ldap_connection().add(dn, attrs)
        return 1

    def _execute_update(self, sql: str, params: Optional[List]) -> int:
        """Execute UPDATE query - modifies LDAP entry."""
        import re

        # Parse UPDATE table SET cols = vals WHERE condition
        match = re.match(
            r"UPDATE\s+(\w+)\s+SET\s+(.+?)\s+WHERE\s+(.+)",
            sql, re.IGNORECASE
        )
        if not match:
            raise NotImplementedError(f"Cannot parse UPDATE: {sql}")

        table_name = match.group(1)
        set_clause = match.group(2)
        where_clause = match.group(3)

        # Find the DN to update from WHERE clause
        dn = None
        if "dn =" in where_clause.lower():
            match_dn = re.search(r"dn\s*=\s*'([^']+)'", where_clause, re.IGNORECASE)
            if match_dn:
                dn = match_dn.group(1)

        # Parse SET clause to get modifications
        set_parts = [s.strip() for s in set_clause.split(',')]
        mods = []
        for part in set_parts:
            col, val = part.split('=')
            ldap_attr = self._column_to_ldap_attr(table_name, col.strip())
            val = self._parse_value(val.strip())
            if isinstance(val, list):
                mods.append((ldap.MOD_REPLACE, ldap_attr, val))
            else:
                mods.append((ldap.MOD_REPLACE, ldap_attr, [val]))

        # Apply modifications
        get_ldap_connection().modify(dn, {k: [(m[0], m[1], m[2])] for m in mods})
        return 1

    def _execute_delete(self, sql: str, params: Optional[List]) -> int:
        """Execute DELETE query - removes LDAP entry."""
        import re

        # Parse DELETE FROM table WHERE condition
        match = re.match(
            r"DELETE\s+FROM\s+(\w+)\s+WHERE\s+(.+)",
            sql, re.IGNORECASE
        )
        if not match:
            raise NotImplementedError(f"Cannot parse DELETE: {sql}")

        table_name = match.group(1)
        where_clause = match.group(2)

        # Extract DN from WHERE clause
        dn = None
        if "dn =" in where_clause.lower():
            match_dn = re.search(r"dn\s*=\s*'([^']+)'", where_clause, re.IGNORECASE)
            if match_dn:
                dn = match_dn.group(1)

        if not dn:
            raise ValueError("Cannot determine DN - need dn condition")

        # Delete entry
        get_ldap_connection().delete(dn)
        return 1

    def _table_to_dn(self, table_name: str) -> str:
        """Convert Django table name to LDAP base DN."""
        mapping = {
            'ldap_users': getattr(settings, 'LDAP_OU_USERS', 'ou=users') + ',' + settings.LDAP_BASE_DN,
            'ldap_posix_groups': getattr(settings, 'LDAP_OU_GROUPS', 'ou=groups') + ',' + settings.LDAP_BASE_DN,
            'ldap_computers': getattr(settings, 'LDAP_OU_COMPUTERS', 'ou=computers') + ',' + settings.LDAP_BASE_DN,
            'ldap_dns_zones': getattr(settings, 'LDAP_OU_DNS', 'ou=dns') + ',' + settings.LDAP_BASE_DN,
            # Add more as needed
        }
        return mapping.get(table_name.lower(), settings.LDAP_BASE_DN)

    def _column_to_ldap_attr(self, table: str, column: str) -> str:
        """Convert Django column name to LDAP attribute."""
        mapping = {
            'cn': 'cn',
            'uid': 'uid',
            'mail': 'mail',
            'sn': 'sn',
            'given_name': 'givenName',
            'home_directory': 'homeDirectory',
            'login_shell': 'loginShell',
            'gid_number': 'gidNumber',
            'uid_number': 'uidNumber',
            'description': 'description',
        }
        return mapping.get(column.lower(), column.replace('_', ''))

    def _where_to_filter(self, where_clause: str) -> str:
        """Convert WHERE clause to LDAP filter."""
        # Simple conversion - handle basic equality
        import re

        # Handle "dn = 'value'"
        dn_match = re.search(r"dn\s*=\s*'([^']+)'", where_clause, re.IGNORECASE)
        if dn_match:
            return f"(dn={self._escape_filter(dn_match.group(1))})"

        # Handle column = value
        eq_match = re.search(r"(\w+)\s*=\s*'([^']+)'", where_clause)
        if eq_match:
            col = self._column_to_ldap_attr("", eq_match.group(1))
            val = self._escape_filter(eq_match.group(2))
            return f"({col}={val})"

        return "(objectClass=*)"

    def _parse_value(self, value: str) -> Any:
        """Parse a SQL value string to Python type."""
        value = value.strip()
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value

    def _escape_rdn(self, value: str) -> str:
        """Escape a value for use in RDN (cn=, uid=)."""
        # LDAP RDN escaping
        value = value.replace('\\', '\\\\')
        value = value.replace(',', '\\,')
        value = value.replace('+', '\\+')
        value = value.replace('<', '\\<')
        value = value.replace('>', '\\>')
        value = value.replace(';', '\\;')
        value = value.replace('=', '\\=')
        value = value.replace('"', '\\"')
        return value

    def _escape_filter(self, value: str) -> str:
        """Escape a value for use in LDAP filter."""
        value = value.replace('\\', '\\5c')
        value = value.replace('*', '\\2a')
        value = value.replace('(', '\\28')
        value = value.replace(')', '\\29')
        value = value.replace('\x00', '\\00')
        return value

    def _format_results(self, results: List[Tuple[str, Dict]]) -> List[Dict]:
        """Format LDAP search results as list of dicts."""
        formatted = []
        for dn, attrs in results:
            entry = {'dn': dn}
            for attr, values in attrs.items():
                if isinstance(values, list):
                    if len(values) == 1:
                        entry[attr] = values[0]
                    else:
                        entry[attr] = values
                else:
                    entry[attr] = values
            formatted.append(entry)
        return formatted

    def fetchone(self) -> Optional[Dict]:
        """Fetch next row."""
        if hasattr(self, 'result_set') and self.result_set:
            return self.result_set.pop(0)
        return None

    def fetchmany(self, size: int = 0) -> List[Dict]:
        """Fetch multiple rows."""
        if size == 0:
            size = self.default_fetch_size
        result = []
        for _ in range(size):
            row = self.fetchone()
            if row:
                result.append(row)
        return result

    def fetchall(self) -> List[Dict]:
        """Fetch all remaining rows."""
        result = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            result.append(row)
        return result

    @property
    def description(self) -> Optional[List[Tuple]]:
        """Return column descriptions."""
        # For LDAP, we don't have fixed columns, so return None
        # This is used by Django for result set metadata
        if hasattr(self, 'result_set') and self.result_set:
            if self.result_set:
                keys = list(self.result_set[0].keys())
                return [(k, None, None, None, None, None, None) for k in keys]
        return []
