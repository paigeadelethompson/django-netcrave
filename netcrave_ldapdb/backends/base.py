"""
Django LDAP Database Backend - Base module.
"""

import ldap
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.utils import CursorWrapper


# Global connection cache
_connection_cache: Dict[str, 'LDAPConnection'] = {}


class LDAPConnection:
    """Simplified LDAP connection wrapper."""

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
               attrs: List[str] = None) -> List[tuple]:
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


def get_ldap_connection() -> 'LDAPConnection':
    """Get or create the global LDAP connection."""
    alias = getattr(settings, 'DATABASE_ALIAS', 'default')
    if alias not in _connection_cache:
        _connection_cache[alias] = LDAPConnection()
    return _connection_cache[alias]


class Cursor(CursorWrapper):
    """LDAP cursor that implements Django's database cursor interface."""

    def __init__(self, connection):
        super().__init__(connection)
        self.connection = connection
        self._result_set: List[Dict] = []
        self.default_fetch_size = 100

    def execute(self, sql: str, params: Optional[List] = None) -> None:
        """Execute an SQL-like query against LDAP."""
        from netcrave_ldapdb.backends import get_ldap_connection

        sql_upper = sql.strip().upper()

        if sql_upper.startswith('SELECT'):
            self._result_set = self._execute_select(sql, params)
        elif sql_upper.startswith('INSERT'):
            self._result_set = [self._execute_insert(sql, params)]
        elif sql_upper.startswith('UPDATE'):
            self._result_set = [self._execute_update(sql, params)]
        elif sql_upper.startswith('DELETE'):
            self._result_set = [self._execute_delete(sql, params)]
        else:
            raise NotImplementedError(f"Unsupported SQL: {sql}")

    def _execute_select(self, sql: str, params: Optional[List]) -> List[Dict]:
        """Execute SELECT query against LDAP."""
        from netcrave_ldapdb.backends import get_ldap_connection

        where_clause = ""
        if "WHERE" in sql.upper():
            parts = sql.upper().split("WHERE", 1)
            where_clause = parts[1].strip()

        from_match = sql.upper().find("FROM")
        if from_match > 0:
            rest = sql[from_match + 4:].strip()
            table_name = rest.split()[0] if rest else ""
        else:
            table_name = ""

        base_dn = self._table_to_dn(table_name)

        ldap_filter = "(objectClass=*)"
        if where_clause:
            ldap_filter = self._where_to_filter(where_clause)

        conn = get_ldap_connection()
        results = conn.search(
            base_dn=base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=ldap_filter,
            attrs=['*', '+']
        )

        return self._format_results(results)

    def _execute_insert(self, sql: str, params: Optional[List]) -> Dict:
        """Execute INSERT query - creates LDAP entry."""
        from netcrave_ldapdb.backends import get_ldap_connection
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

        attrs = {}
        for col, val in zip(columns, values):
            ldap_attr = self._column_to_ldap_attr(table_name, col)
            if isinstance(val, list):
                attrs[ldap_attr] = val
            else:
                attrs[ldap_attr] = [val]

        cn_value = attrs.get('cn', [None])[0]
        uid_value = attrs.get('uid', [None])[0]
        base_dn = self._table_to_dn(table_name)

        if cn_value:
            dn = f"cn={self._escape_rdn(cn_value)},{base_dn}"
        elif uid_value:
            dn = f"uid={self._escape_rdn(uid_value)},{base_dn}"
        else:
            raise ValueError("Cannot determine DN - missing cn or uid")

        if 'objectClass' not in attrs:
            attrs['objectClass'] = ['top']

        conn = get_ldap_connection()
        conn.add(dn, attrs)

        return {'dn': dn}

    def _execute_update(self, sql: str, params: Optional[List]) -> Dict:
        """Execute UPDATE query - modifies LDAP entry."""
        from netcrave_ldapdb.backends import get_ldap_connection
        import re

        match = re.match(
            r"UPDATE\s+(\w+)\s+SET\s+(.+?)\s+WHERE\s+(.+)",
            sql, re.IGNORECASE
        )
        if not match:
            raise NotImplementedError(f"Cannot parse UPDATE: {sql}")

        table_name = match.group(1)
        set_clause = match.group(2)
        where_clause = match.group(3)

        dn = None
        if "dn =" in where_clause.lower():
            match_dn = re.search(r"dn\s*=\s*'([^']+)'", where_clause, re.IGNORECASE)
            if match_dn:
                dn = match_dn.group(1)

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

        conn = get_ldap_connection()
        conn.modify(dn, {k: [(m[0], m[1], m[2])] for m in mods})

        return {'dn': dn}

    def _execute_delete(self, sql: str, params: Optional[List]) -> Dict:
        """Execute DELETE query - removes LDAP entry."""
        from netcrave_ldapdb.backends import get_ldap_connection
        import re

        match = re.match(
            r"DELETE\s+FROM\s+(\w+)\s+WHERE\s+(.+)",
            sql, re.IGNORECASE
        )
        if not match:
            raise NotImplementedError(f"Cannot parse DELETE: {sql}")

        table_name = match.group(1)
        where_clause = match.group(2)

        dn = None
        if "dn =" in where_clause.lower():
            match_dn = re.search(r"dn\s*=\s*'([^']+)'", where_clause, re.IGNORECASE)
            if match_dn:
                dn = match_dn.group(1)

        if not dn:
            raise ValueError("Cannot determine DN - need dn condition")

        conn = get_ldap_connection()
        conn.delete(dn)

        return {'dn': dn}

    def _table_to_dn(self, table_name: str) -> str:
        """Convert Django table name to LDAP base DN."""
        mapping = {
            'ldap_users': getattr(settings, 'LDAP_OU_USERS', 'ou=users') + ',' + settings.LDAP_BASE_DN,
            'ldap_posix_groups': getattr(settings, 'LDAP_OU_GROUPS', 'ou=groups') + ',' + settings.LDAP_BASE_DN,
            'ldap_computers': getattr(settings, 'LDAP_OU_COMPUTERS', 'ou=computers') + ',' + settings.LDAP_BASE_DN,
            'ldap_dns_zones': getattr(settings, 'LDAP_OU_DNS', 'ou=dns') + ',' + settings.LDAP_BASE_DN,
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
        import re

        dn_match = re.search(r"dn\s*=\s*'([^']+)'", where_clause, re.IGNORECASE)
        if dn_match:
            return f"(dn={self._escape_filter(dn_match.group(1))})"

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
        """Escape a value for use in RDN."""
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

    def _format_results(self, results: List[tuple]) -> List[Dict]:
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
        if self._result_set:
            return self._result_set.pop(0)
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
    def description(self) -> Optional[List[tuple]]:
        """Return column descriptions."""
        if self._result_set:
            keys = list(self._result_set[0].keys())
            return [(k, None, None, None, None, None, None) for k in keys]
        return []


class DatabaseClient:
    """Dummy client - LDAP doesn't have a separate client."""

    def __init__(self, connection):
        self.connection = connection


class DatabaseCreation:
    """Dummy creation manager - LDAP has no DDL like SQL."""

    def __init__(self, connection):
        self.connection = connection

    def create_test_db(self, *args, **kwargs):
        return "test_db"

    def destroy_test_db(self, *args, **kwargs):
        pass


class DatabaseFeatures:
    """LDAP database features."""

    def __init__(self, connection):
        self.connection = connection

    supports_transactions = False
    supports_savepoints = False
    can_return_columns_from_insert = False
    empty_fetchmany_value = []


class DatabaseIntrospection:
    """LDAP database introspection."""

    def __init__(self, connection):
        self.connection = connection

    def get_table_list(self, cursor):
        return []

    def get_table_description(self, cursor, table_name):
        return []

    def get_relations(self, cursor, table_name):
        return {}

    def get_indexes(self, cursor, table_name):
        return {}

    def get_constraints(self, cursor, table_name):
        return {}


class DatabaseOperations:
    """LDAP database operations."""

    compiler_module = "netcrave_ldapdb.backends.compiler"

    def __init__(self, connection):
        self.connection = connection

    def quote_name(self, name):
        return name.strip('"\'`')

    def bulk_insert_sql(self, *args, **kwargs):
        return ''

    def combine_expression(self, connector, sub_expressions):
        if connector == 'AND':
            return '(%s)' % ' AND '.join(sub_expressions)
        elif connector == 'OR':
            return '(%s)' % ' OR '.join(sub_expressions)
        return '(%s)' % f' {connector} '.join(sub_expressions)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        if isinstance(value, (list, tuple)):
            return list(value)
        return str(value)

    def regex_lookup(self, lookup_type):
        return '%s'

    def year_lookup_bounds_for_datetime_field(self, value):
        from datetime import datetime
        first = datetime(value, 1, 1)
        last = datetime(value, 12, 31, 23, 59, 59)
        return [first, last]

    def max_in_list_size(self):
        return 0

    def max_name_length(self):
        """Return maximum name length."""
        return 30


class DatabaseValidation:
    """LDAP database validation."""

    def __init__(self, connection):
        self.connection = connection

    def validate_field(self, *args, **kwargs):
        pass

    def validate_model(self, *args, **kwargs):
        pass


class DatabaseWrapper(BaseDatabaseWrapper):
    """Django database wrapper for LDAP backend."""

    vendor = 'ldap'
    display_name = 'LDAP'

    # Required class attributes
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
    validation_class = DatabaseValidation

    # Data type mappings
    data_types = {
        'AutoField': 'INTEGER',
        'BigAutoField': 'INTEGER',
        'SmallAutoField': 'INTEGER',
        'BigIntegerField': 'INTEGER',
        'BooleanField': 'BOOLEAN',
        'CharField': 'IA5String',
        'DateField': 'GeneralizedTime',
        'DateTimeField': 'GeneralizedTime',
        'DecimalField': 'STRING',
        'EmailField': 'IA5String',
        'GenericIPAddressField': 'IA5String',
        'IntegerField': 'INTEGER',
        'PositiveBigIntegerField': 'INTEGER',
        'PositiveIntegerField': 'INTEGER',
        'PositiveSmallIntegerField': 'INTEGER',
        'SlugField': 'IA5String',
        'SmallIntegerField': 'INTEGER',
        'TextField': 'STRING',
        'TimeField': 'GeneralizedTime',
    }

    def __init__(self, settings_dict, alias='default'):
        super().__init__(settings_dict, alias)
        self.ldap_connection = None

    def get_ldap_connection(self):
        """Get the LDAP connection for this wrapper."""
        if self.ldap_connection is None:
            self.ldap_connection = LDAPConnection()
        return self.ldap_connection

    def get_new_connection(self, conn_params):
        """Create a new connection."""
        conn = LDAPConnection()
        if 'LDAP_SERVER_URI' in conn_params:
            conn.server_uri = conn_params['LDAP_SERVER_URI']
        if 'LDAP_BASE_DN' in conn_params:
            conn.base_dn = conn_params['LDAP_BASE_DN']
        if 'LDAP_BIND_DN' in conn_params:
            conn.bind_dn = conn_params['LDAP_BIND_DN']
        if 'LDAP_BIND_PASSWORD' in conn_params:
            conn.bind_password = conn_params['LDAP_BIND_PASSWORD']
        return conn

    def init_connection_state(self):
        """Initialize connection state."""
        pass

    def create_cursor(self, name=None):
        """Create a new cursor."""
        return Cursor(self)

    def _set_autocommit(self, autocommit):
        """Set autocommit mode."""
        pass

    def begin(self):
        """Start a transaction."""
        pass

    def commit(self):
        """Commit a transaction."""
        pass

    def rollback(self):
        """Rollback a transaction."""
        pass

    def close(self):
        """Close the connection."""
        if self.ldap_connection:
            self.ldap_connection.disconnect()
            self.ldap_connection = None

    def check_constraints(self, table_names=None):
        """Check constraints."""
        pass

    def disable_constraint_checking(self):
        """Disable constraint checking."""
        return False

    def enable_constraint_checking(self):
        """Enable constraint checking."""
        pass

    def is_usable(self):
        """Check if connection is usable."""
        try:
            if self.ldap_connection and self.ldap_connection.conn:
                self.ldap_connection.search(
                    self.settings_dict.get('LDAP_BASE_DN', 'dc=example,dc=com'),
                    ldap.SCOPE_BASE,
                    "(objectClass=*)",
                    ['objectClass']
                )
                return True
            return False
        except Exception:
            return False
