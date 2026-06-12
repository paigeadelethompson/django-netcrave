"""SQL Compiler module for netcrave_ldapdb backend."""

import logging
from typing import Any, Dict, List, Optional, Tuple

from django.db.models.sql.compiler import SQLCompiler
from django.db.models.sql.constants import MULTI
from django.db.models.sql.where import WhereNode
from django.conf import settings

logger = logging.getLogger(__name__)


class LDAPQuery:
    """LDAP query representation."""

    def __init__(self, model, base_dn: str = None):
        self.model = model
        self.base_dn = base_dn or getattr(model, 'ldap_base_dn', settings.LDAP_BASE_DN)
        self.filter_parts: List[str] = []
        self.attrs: Optional[List[str]] = None
        self.scope = 2

    def add_filter(self, ldap_filter: str) -> None:
        """Add a filter part."""
        self.filter_parts.append(ldap_filter)

    def get_filter(self) -> str:
        """Get combined LDAP filter."""
        if not self.filter_parts:
            return "(objectClass=*)"
        if len(self.filter_parts) == 1:
            return self.filter_parts[0]
        return "(&%s)" % "".join(f"({part})" for part in self.filter_parts)

    def set_attrs(self, attrs: List[str]) -> None:
        """Set attributes to retrieve."""
        self.attrs = attrs

    def get_attrs(self) -> Optional[List[str]]:
        """Get attributes to retrieve."""
        return self.attrs


class LDAPWhereNode(WhereNode):
    """LDAP-specific Where node that converts to filter."""

    def as_ldap(self, compiler, connection) -> str:
        """Convert this node to an LDAP filter."""
        children = [
            child.as_ldap(compiler, connection)
            for child in self.children
        ]
        if not children:
            return "(objectClass=*)"

        if self.connector == 'AND':
            return "(&%s)" % "".join(f"({child})" for child in children)
        elif self.connector == 'OR':
            return "(|%s)" % "".join(f"({child})" for child in children)

        return "(&%s)" % "".join(f"({child})" for child in children)


class LDAPQueryCompiler(SQLCompiler):
    """SQL compiler that generates LDAP filters."""

    def __init__(self, query, connection, using):
        super().__init__(query, connection, using)
        self.query = query
        self.connection = connection

    def pre_sql_setup(self):
        """Do any preprocessing needed before generating SQL."""
        super().pre_sql_setup()

    def as_sql(self) -> Tuple[str, List]:
        """Generate LDAP filter from queryset."""
        ldap_query = self.build_ldap_query()
        ldap_filter = ldap_query.get_filter()
        attrs = ldap_query.get_attrs() or ['*', '+']

        # Return as a pseudo-SQL that our cursor understands
        table_name = self.query.model._meta.db_table
        sql = f"SELECT * FROM {table_name} WHERE LDAP_FILTER='{ldap_filter}'"

        return sql, []

    def build_ldap_query(self) -> LDAPQuery:
        """Build LDAP query from Django queryset."""
        model = self.query.model
        base_dn = getattr(model, 'ldap_base_dn', settings.LDAP_BASE_DN)

        ldap_query = LDAPQuery(model, base_dn)

        if self.query.select_all:
            ldap_query.set_attrs(['*', '+'])
        else:
            attrs = []
            for alias, expr in self.query.annotations.items():
                attrs.append(alias)
            ldap_query.set_attrs(attrs or ['*'])

        # Add filters from where clause
        if self.query.where:
            filter_str = self.query.where.as_ldap(self, self.connection)
            if filter_str and filter_str != "(objectClass=*)":
                ldap_query.add_filter(filter_str)

        return ldap_query

    def execute_sql(self, result_type=MULTI):
        """Execute the query and return results."""
        sql, params = self.as_sql()

        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            if result_type == MULTI:
                return cursor.fetchall()
            else:
                return cursor.fetchone()


class LDAPInsertCompiler(SQLCompiler):
    """Compiler for INSERT statements."""

    def execute_sql(self, return_id=False):
        """Execute insert and optionally return ID."""
        model = self.query.model

        attrs = {}
        for field in model._meta.fields:
            if hasattr(field, 'db_column'):
                ldap_attr = field.db_column
            else:
                ldap_attr = field.name.replace('_', '-')

            value = getattr(self.query.objs[0], field.attname, None)
            if value is not None:
                attrs[ldap_attr] = [str(value)] if not isinstance(value, list) else value

        dn = self.query.objs[0].dn

        return dn


class LDAPUpdateCompiler(SQLCompiler):
    """Compiler for UPDATE statements."""

    pass


class LDAPDeleteCompiler(SQLCompiler):
    """Compiler for DELETE statements."""

    def execute_sql(self, result_type=MULTI):
        """Execute delete and return count."""
        model = self.query.model
        dn = self.query.objs[0].dn if hasattr(self.query, 'objs') else None

        if dn:
            return 1
        return 0
