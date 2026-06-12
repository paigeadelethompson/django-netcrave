"""
LDAP models for OpenLDAP Java schema.

This module provides:
- javaContainer: Container for a Java object (STRUCTURAL)
- javaObject: Abstract base class for Java objects
- javaSerializedObject: Auxiliary class for serialized Java objects
- javaMarshalledObject: Auxiliary class for marshalled Java objects
- javaNamingReference: Auxiliary class for JNDI references
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class JavaContainer(LDAPModel):
    """Java Container.

    Based on java.schema javaContainer.
    STRUCTURAL object class.

    MUST: cn
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="containerName",
        help_text="Container name (cn)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this Java container",
    )

    ldap_base_dn = settings.LDAP_OU_JAVA + "," + settings.LDAP_BASE_DN
    object_classes = ["javaContainer"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_java_container"
        verbose_name = "Java Container"
        verbose_name_plural = "Java Containers"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this Java container."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_JAVA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class JavaObject(LDAPModel):
    """Java Object (abstract base).

    Based on java.schema javaObject.
    ABSTRACT object class.

    MUST: javaClassName
    MAY: javaClassNames, javaCodebase, javaDoc, description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="objectName",
        help_text="Object name (cn)",
    )
    java_class_name = models.CharField(
        max_length=255,
        verbose_name="javaClassName",
        help_text="Java class name (must be specified)",
    )
    java_class_names = models.JSONField(
        blank=True,
        default=list,
        verbose_name="javaClassNames",
        help_text="List of Java class names",
    )
    java_codebase = models.TextField(
        blank=True,
        null=True,
        verbose_name="javaCodebase",
        help_text="URL(s) for loading classes",
    )
    java_doc = models.TextField(
        blank=True,
        null=True,
        verbose_name="javaDoc",
        help_text="Documentation for this Java object",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this Java object",
    )

    ldap_base_dn = settings.LDAP_OU_JAVA + "," + settings.LDAP_BASE_DN
    object_classes = ["javaObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'java_class_name': 'javaClassName',
        'java_class_names': 'javaClassNames',
        'java_codebase': 'javaCodebase',
        'java_doc': 'javaDoc',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_java_object"
        verbose_name = "Java Object"
        verbose_name_plural = "Java Objects"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this Java object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_JAVA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class JavaSerializedObject(LDAPModel):
    """Java Serialized Object (AUXILIARY).

    Based on java.schema javaSerializedObject.
    AUXILIARY object class.

    MUST: javaSerializedData
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="serializedName",
        help_text="Serialized name (cn)",
    )
    java_serialized_data = models.TextField(
        verbose_name="javaSerializedData",
        help_text="Base64-encoded serialized Java object data",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this Java serialized object",
    )

    ldap_base_dn = settings.LDAP_OU_JAVA + "," + settings.LDAP_BASE_DN
    object_classes = ["javaSerializedObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'java_serialized_data': 'javaSerializedData',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_java_serialized"
        verbose_name = "Java Serialized Object"
        verbose_name_plural = "Java Serialized Objects"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this Java serialized object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_JAVA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class JavaMarshalledObject(LDAPModel):
    """Java Marshalled Object (AUXILIARY).

    Based on java.schema javaMarshalledObject.
    AUXILIARY object class.

    MUST: javaSerializedData
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="marshalledName",
        help_text="Marshalled name (cn)",
    )
    java_serialized_data = models.TextField(
        verbose_name="javaSerializedData",
        help_text="Base64-encoded marshalled Java object data",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this Java marshalled object",
    )

    ldap_base_dn = settings.LDAP_OU_JAVA + "," + settings.LDAP_BASE_DN
    object_classes = ["javaMarshalledObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'java_serialized_data': 'javaSerializedData',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_java_marshalled"
        verbose_name = "Java Marshalled Object"
        verbose_name_plural = "Java Marshalled Objects"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this Java marshalled object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_JAVA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class JavaNamingReference(LDAPModel):
    """Java Naming Reference (JNDI, AUXILIARY).

    Based on java.schema javaNamingReference.
    AUXILIARY object class.

    MAY: javaReferenceAddress, javaFactory
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="referenceName",
        help_text="Reference name (cn)",
    )
    java_reference_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="javaReferenceAddress",
        help_text="JNDI reference address",
    )
    java_factory = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="javaFactory",
        help_text="Java factory class for creating the object",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this Java naming reference",
    )

    ldap_base_dn = settings.LDAP_OU_JAVA + "," + settings.LDAP_BASE_DN
    object_classes = ["javaNamingReference"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'java_reference_address': 'javaReferenceAddress',
        'java_factory': 'javaFactory',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_java_naming"
        verbose_name = "Java Naming Reference"
        verbose_name_plural = "Java Naming References"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this Java naming reference."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_JAVA)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
