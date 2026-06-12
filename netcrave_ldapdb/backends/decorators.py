"""
Decorators for automatically generating LDAP attributes from Django model fields.
"""

import re
from typing import Any, Dict


def ldap_attributes_map(**field_mapping):
    """
    Decorator that automatically generates get_ldap_attributes() method
    based on field mappings and the model's object_classes.

    Usage:
        @ldap_attributes_map(
            cn='cn',
            uid='uid',
            mail='mail',
            description='description'
        )
        class MyModel(LDAPModel):
            ...

    The decorator will create a get_ldap_attributes() method that:
    1. Sets 'objectClass' to the model's object_classes list
    2. Maps each Django field to its LDAP attribute name
    3. Handles list/JSONField values appropriately

    Args:
        **field_mapping: Keyword args mapping field_name -> ldap_attribute_name

    Returns:
        Decorator function
    """
    def decorator(cls):
        # Get existing object_classes if defined, otherwise use ['top']
        original_object_classes = getattr(cls, 'object_classes', [])

        def get_ldap_attributes(self) -> Dict[str, Any]:
            """Auto-generated LDAP attributes from Django fields."""
            attrs: Dict[str, Any] = {
                "objectClass": list(original_object_classes),
            }

            for field_name, ldap_attr in field_mapping.items():
                value = getattr(self, field_name, None)
                if value is not None:
                    # Handle JSONField/list values
                    if isinstance(value, (list, tuple)):
                        attrs[ldap_attr] = list(value)
                    else:
                        # Convert to string for single values
                        attrs[ldap_attr] = [str(value)]
                elif hasattr(self, field_name) and getattr(self, field_name, None) is not None:
                    # Field exists but might be empty - handle based on type
                    pass

            return attrs

        cls.get_ldap_attributes = get_ldap_attributes
        return cls

    return decorator


def ldap_auto_attrs(cls):
    """
    Decorator that automatically generates LDAP attributes by introspecting
    the model's fields and using field names as LDAP attribute names (with
    underscores converted to hyphens).

    This is a simpler approach than ldap_attributes_map - it uses:
    - The model's object_classes for 'objectClass'
    - Field db_column or name -> LDAP attr (snake_case -> kebab-case)
    """
    original_object_classes = getattr(cls, 'object_classes', [])

    def get_ldap_attributes(self) -> Dict[str, Any]:
        """Auto-generated LDAP attributes from field introspection."""
        attrs: Dict[str, Any] = {
            "objectClass": list(original_object_classes),
        }

        for field in self._meta.get_fields():
            # Skip non-attribute fields
            if field.many_to_many or field.one_to_many:
                continue

            # Get the LDAP attribute name
            ldap_attr = getattr(field, 'db_column', None) or field.name.replace('_', '-')

            value = getattr(self, field.name, None)
            if value is not None:
                # Handle list/JSONField values
                if isinstance(value, (list, tuple)):
                    attrs[ldap_attr] = list(value)
                else:
                    attrs[ldap_attr] = [str(value)]

        return attrs

    cls.get_ldap_attributes = get_ldap_attributes
    return cls


def convert_field_to_ldap_attr(field_name: str) -> str:
    """Convert Django field name to LDAP attribute name."""
    # Keep explicit db_column if set
    # Otherwise snake_case -> kebab-case
    return field_name.replace('_', '-')
