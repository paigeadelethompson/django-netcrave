"""
Base LDAP model and manager classes with python-ldap integration.
"""

from typing import Any, Dict, List, Optional

import ldap
from django.conf import settings
from django.db import models

# Import the LDAP backend
try:
    from ..utils.ldap_backend import get_ldap_connection
except ImportError:
    # Fallback for development without python-ldap installed
    def get_ldap_connection():
        raise NotImplementedError("python-ldap not available")


class LDAPManager(models.Manager):
    """Custom manager for LDAP models with DN helper methods."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connection = None

    @property
    def connection(self):
        """Get or create LDAP connection."""
        if not self._connection:
            from ..utils.ldap_backend import get_ldap_connection
            self._connection = get_ldap_connection()
        return self._connection

    def get_queryset(self):
        """Get the base queryset."""
        return super().get_queryset()

    def get_by_dn(self, dn: str) -> Optional[models.Model]:
        """Get an entry by its distinguished name.

        Args:
            dn: The full DN string

        Returns:
            Model instance or None if not found
        """
        try:
            return self.get(dn=dn)
        except self.model.DoesNotExist:
            return None


class CounterManager(LDAPManager):
    """Manager for counter objects used to auto-increment IDs."""

    def get_next_uid_number(self) -> int:
        """Get and increment the next UID number.

        Returns:
            The next available UID number
        """
        from .base import LDAPCounter

        counter, _ = LDAPCounter.objects.get_or_create(
            key=LDAPCounter.UID_COUNTER_KEY,
            defaults={"value": settings.LDAP_DEFAULT_UID_NUMBER},
        )
        value = counter.value
        counter.value += 1
        counter.save(update_fields=["value"])
        return value

    def get_next_gid_number(self) -> int:
        """Get and increment the next GID number.

        Returns:
            The next available GID number
        """
        from .base import LDAPCounter

        counter, _ = LDAPCounter.objects.get_or_create(
            key=LDAPCounter.GID_COUNTER_KEY,
            defaults={"value": settings.LDAP_DEFAULT_GID_NUMBER},
        )
        value = counter.value
        counter.value += 1
        counter.save(update_fields=["value"])
        return value


class LDAPModel(models.Model):
    """Abstract base model for all LDAP-backed models.

    Provides common functionality:
    - Automatic DN construction
    - Object class management
    - Schema compliance
    - python-ldap integration

    Subclasses should define:
    - ldap_base_dn: Base DN for this model type
    - object_classes: List of required LDAP object classes
    - ldap_attributes_map: Mapping from Django fields to LDAP attributes (required)
    """

    # Base distinguished name (can be overridden per model)
    ldap_base_dn: Optional[str] = None

    # List of object classes this entry will have
    object_classes: List[str] = []

    # Attributes that are part of the primary key in LDAP
    ldap_pk_attributes: List[str] = []

    # Mapping from Django field names to LDAP attribute names (REQUIRED)
    ldap_attributes_map: Dict[str, str]

    class Meta:
        abstract = True

    def __str__(self) -> str:
        """Return string representation."""
        return self.get_dn()

    @property
    def dn(self) -> str:
        """Get the full distinguished name for this entry.

        This property should be overridden by subclasses to provide
        the correct DN construction based on their attributes.
        """
        raise NotImplementedError("Subclasses must implement dn property")

    def get_dn(self) -> str:
        """Get the full distinguished name."""
        return self.dn

    @classmethod
    def get_base_dn(cls) -> str:
        """Get the base DN for this model type."""
        if cls.ldap_base_dn:
            return cls.ldap_base_dn
        raise NotImplementedError("Subclasses must implement ldap_base_dn or get_base_dn()")

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get all object classes for this model."""
        return cls.object_classes.copy()

    def get_ldap_attributes(self) -> Dict[str, Any]:
        """Get a dictionary of LDAP attributes for this entry.

        Uses the ldap_attributes_map class property to map Django field names
        to LDAP attribute names. The mapping is explicit (no conversion).
        """
        attrs: Dict[str, Any] = {
            "objectClass": list(self.get_object_classes()),
        }

        # Use the model's ldap_attributes_map for field-to-attribute conversion
        for field_name, ldap_attr in self.ldap_attributes_map.items():
            value = getattr(self, field_name, None)
            if value is not None:
                # Handle list/JSONField values
                if isinstance(value, (list, tuple)):
                    attrs[ldap_attr] = list(value)
                else:
                    attrs[ldap_attr] = [str(value)]

        return attrs

    @classmethod
    def normalize_dn(cls, dn: str) -> str:
        """Normalize a DN string (lowercase keys, consistent format)."""
        parts = []
        for part in dn.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                parts.append(f"{key.strip().lower()}={value.strip()}")
            else:
                parts.append(part)
        return ",".join(parts)

    def clean(self) -> None:
        """Validate the model instance before saving."""
        super().clean()
        self._validate_object_classes()

    def _validate_object_classes(self) -> None:
        """Validate that all required object classes are present.

        Override this method in subclasses to add custom validation.
        """
        pass

    # ==================================================================
    # LDAP CRUD Operations
    # ==================================================================

    def ldap_exists(self, connection=None) -> bool:
        """Check if this entry exists in LDAP."""
        if connection is None:
            connection = get_ldap_connection()

        try:
            result = connection.search(self.dn, ldap.SCOPE_BASE, "(objectClass=*)")
            return len(result) > 0
        except ldap.NO_SUCH_OBJECT:
            return False
        except Exception:
            return False

    def ldap_create(self, connection=None) -> bool:
        """Create this entry in LDAP.

        Args:
            connection: Optional pre-established LDAP connection

        Returns:
            True if successful, False if already exists
        """
        if connection is None:
            connection = get_ldap_connection()

        try:
            attributes = self.get_ldap_attributes()
            # Ensure objectClass attribute is present
            if 'objectClass' not in attributes:
                attributes['objectClass'] = self.object_classes

            return connection.add(self.dn, attributes)
        except ldap.ALREADY_EXISTS:
            return False
        except Exception as e:
            raise

    def ldap_read(self, connection=None) -> Dict[str, Any]:
        """Read this entry from LDAP.

        Args:
            connection: Optional pre-established LDAP connection

        Returns:
            Dictionary of LDAP attributes
        """
        if connection is None:
            connection = get_ldap_connection()

        result = connection.get(self.dn)
        return dict(result[1]) if result else {}

    def ldap_update(self, changes: Dict[str, Any], connection=None) -> bool:
        """Update this entry in LDAP.

        Args:
            changes: Dictionary of attribute names to new values
            connection: Optional pre-established LDAP connection

        Returns:
            True if successful
        """
        if connection is None:
            connection = get_ldap_connection()

        # Build modlist from changes
        modlist = []
        for attr, value in changes.items():
            if value is None:
                # Delete attribute
                modlist.append((ldap.MOD_DELETE, attr, None))
            else:
                # Replace attribute
                modlist.append((ldap.MOD_REPLACE, attr, value))

        return connection.modify(self.dn, {attr: [(op, attr, val) for op, attr, val in modlist]})

    def ldap_delete(self, connection=None) -> bool:
        """Delete this entry from LDAP.

        Args:
            connection: Optional pre-established LDAP connection

        Returns:
            True if successful
        """
        if connection is None:
            connection = get_ldap_connection()

        return connection.delete(self.dn)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the model instance to both database and LDAP."""
        self.full_clean()
        # Save to Django database first (for auto IDs)
        super().save(*args, **kwargs)


class LDAPCounter(LDAPModel):
    """Counter object for auto-incrementing IDs.

    This model stores the current values of various counters in LDAP,
    allowing Django to generate unique uidNumber and gidNumber values.
    """

    UID_COUNTER_KEY = "uidNumber"
    GID_COUNTER_KEY = "gidNumber"

    key = models.CharField(max_length=50, primary_key=True)
    value = models.PositiveIntegerField(default=1000)

    ldap_base_dn = settings.LDAP_COUNTER_BASE_DN
    object_classes = ["simpleSecurityObject"]

    class Meta:
        db_table = "ldap_counters"
        verbose_name = "LDAP Counter"
        verbose_name_plural = "LDAP Counters"

    def __str__(self) -> str:
        return f"{self.key} = {self.value}"
