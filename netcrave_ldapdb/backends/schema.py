"""Schema module for netcrave_ldapdb backend."""

from typing import Any, Dict, List, Optional, Tuple

from django.db.models.fields import (
    AutoField, BigIntegerField, BooleanField, CharField, DateField,
    DateTimeField, DecimalField, EmailField, Field, IntegerField,
    GenericIPAddressField, PositiveIntegerField, SlugField, SmallIntegerField,
    TextField, TimeField, URLField
)


def django_field_to_ldap_attr(field: Field) -> Tuple[str, str]:
    """
    Convert a Django field to LDAP attribute specification.

    Returns:
        tuple: (ldap_attribute_name, python_type)
    """
    if hasattr(field, 'db_column') and field.db_column:
        ldap_attr = field.db_column
    else:
        ldap_attr = field.name.replace('_', '-')

    ldap_type = 'IA5String'

    if isinstance(field, (IntegerField, AutoField, PositiveIntegerField,
                          SmallIntegerField, BigIntegerField)):
        ldap_type = 'INTEGER'
    elif isinstance(field, BooleanField):
        ldap_type = 'BOOLEAN'
    elif isinstance(field, (DateField, DateTimeField)):
        ldap_type = 'GeneralizedTime'
    elif isinstance(field, DecimalField):
        ldap_type = 'STRING'
    elif isinstance(field, EmailField):
        ldap_type = 'IA5String'
    elif isinstance(field, GenericIPAddressField):
        ldap_type = 'IA5String'

    return ldap_attr, ldap_type


def convert_ldap_value(value: Any, field_type: str) -> Any:
    """
    Convert an LDAP attribute value to the appropriate Python type.

    Args:
        value: The LDAP attribute value (may be list)
        field_type: The LDAP syntax/type

    Returns:
        Converted Python value
    """
    if isinstance(value, list):
        if len(value) == 0:
            return None
        if len(value) == 1:
            value = value[0]
        else:
            return [convert_ldap_value(v, field_type) for v in value]

    if value is None:
        return None

    if field_type == 'INTEGER':
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    elif field_type == 'BOOLEAN':
        if isinstance(value, bool):
            return value
        return str(value).upper() in ('TRUE', 'YES', '1')
    elif field_type == 'GeneralizedTime':
        from datetime import datetime
        try:
            return datetime.strptime(str(value), "%Y%m%d%H%M%SZ")
        except ValueError:
            return value
    else:
        return str(value)


def get_ldap_object_classes(model) -> List[str]:
    """Get the LDAP object classes for a Django model."""
    if hasattr(model, 'object_classes'):
        return list(model.object_classes)
    return ['top', 'inetOrgPerson']


def build_ldap_filter(field: Field, value: Any, lookup_type: str = 'exact') -> str:
    """
    Build an LDAP filter from a Django field and value.

    Args:
        field: The Django field
        value: The value to filter on
        lookup_type: The Django lookup type

    Returns:
        LDAP filter string
    """
    ldap_attr, _ = django_field_to_ldap_attr(field)

    if value is None:
        if lookup_type == 'isnull':
            return f"(!({ldap_attr}=*))" if value else f"({ldap_attr}=*)"
        return f"(!({ldap_attr}=*))"

    escaped = str(value)
    escaped = escaped.replace('\\', '\\5c')
    escaped = escaped.replace('*', '\\2a')
    escaped = escaped.replace('(', '\\28')
    escaped = escaped.replace(')', '\\29')

    if lookup_type == 'exact':
        return f"({ldap_attr}={escaped})"
    elif lookup_type == 'contains':
        return f"({ldap_attr}=*{escaped}*)"
    elif lookup_type == 'icontains':
        return f"({ldap_attr}=*{str(value).lower()}*)"
    elif lookup_type == 'startswith':
        return f"({ldap_attr}={escaped}*)"
    elif lookup_type == 'istartswith':
        return f"({ldap_attr}=*{str(value).lower()}*)"
    elif lookup_type == 'endswith':
        return f"({ldap_attr}=*{escaped})"
    elif lookup_type == 'iendswith':
        return f"({ldap_attr}=*{str(value).lower()})"
    elif lookup_type == 'gte':
        return f"({ldap_attr}>={escaped})"
    elif lookup_type == 'lte':
        return f"({ldap_attr}<={escaped})"
    elif lookup_type == 'gt':
        return f"({ldap_attr}>{escaped})"
    elif lookup_type == 'lt':
        return f"({ldap_attr}<{escaped})"

    return f"({ldap_attr}={escaped})"


class LDAPSchemaEditor:
    """Schema editor for LDAP-backed Django models."""

    def __init__(self, connection):
        self.connection = connection

    def create_model(self, model) -> None:
        """Create a new LDAP entry type."""
        pass

    def delete_model(self, model) -> None:
        """Delete all entries of a model type."""
        from netcrave_ldapdb.backends import get_ldap_connection

        base_dn = model.ldap_base_dn if hasattr(model, 'ldap_base_dn') else settings.LDAP_BASE_DN
        get_ldap_connection().search(base_dn, filterstr=f"(objectClass={model.__name__})")

    def add_field(self, model, field) -> None:
        """Add a new LDAP attribute to existing entries."""
        pass

    def remove_field(self, model, field) -> None:
        """Remove an attribute (soft delete - set to empty)."""
        pass

    def alter_field(self, model, old_field, new_field) -> None:
        """Change a field's LDAP attribute mapping."""
        pass
