"""
LDAP models for Microsoft user extensions.

This module provides:
- MsUser: Windows user with AD-like attributes
"""

from typing import List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class MsUser(LDAPModel):
    """Windows user model with Microsoft extensions.

    Based on msuser.schema.
    Combines inetOrgPerson with Windows-specific attributes.
    """

    # Core identity (inherited from inetOrgPerson)
    cn = models.CharField(
        max_length=255,
        help_text="Common name",
    )
    sn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Surname",
    )
    given_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="givenName",
        help_text="Given name",
    )
    uid = models.CharField(
        max_length=255,
        unique=True,
        help_text="User login ID (sAMAccountName equivalent)",
    )
    mail = models.EmailField(
        blank=True,
        null=True,
        help_text="Email address",
    )

    # Windows-specific attributes
    s_am_account_name = models.CharField(
        max_length=255,
        verbose_name="sAMAccountName",
        help_text="Windows pre-Windows 2000 login name",
    )
    user_principal_name = models.EmailField(
        blank=True,
        null=True,
        verbose_name="userPrincipalName",
        help_text="User Principal Name (UPN)",
    )

    # Account settings
    account_disabled = models.BooleanField(
        default=False,
        verbose_name="accountDisabled",
        help_text="Whether the account is disabled",
    )
    password_expired = models.BooleanField(
        default=False,
        verbose_name="passwordExpired",
        help_text="Whether the user must change password at next login",
    )
    password_never_expires = models.BooleanField(
        default=False,
        verbose_name="passwordNeverExpires",
        help_text="Whether the password never expires",
    )
    dont_require_pre_auth = models.BooleanField(
        default=False,
        verbose_name="dontRequirePreAuth",
        help_text="Do not require Kerberos pre-authentication",
    )

    # Profile path and logon scripts
    profile_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="profilePath",
        help_text="User's profile path (UNC)",
    )
    logon_script = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="logonScript",
        help_text="Logon script path",
    )
    home_directory = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="homeDirectory",
        help_text="Home directory path",
    )
    home_drive = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="homeDrive",
        help_text="Home drive letter (e.g., 'H:')",
    )

    # Directory service attributes
    object_sid = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="objectSID",
        help_text="Windows Security Identifier (SID)",
    )
    user_account_control = models.PositiveIntegerField(
        default=512,
        verbose_name="userAccountControl",
        help_text="Account control flags (UAC)",
    )

    ldap_base_dn = settings.LDAP_OU_USERS + "," + settings.LDAP_BASE_DN
    object_classes = ["inetOrgPerson", "person"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_ms_users"
        verbose_name = "Windows User (MsUser)"
        verbose_name_plural = "Windows Users"

    def __str__(self) -> str:
        return self.cn or self.uid

    @property
    def dn(self) -> str:
        """Get the DN for this user."""
        from ..utils.dn import build_user_dn

        return build_user_dn(self.s_am_account_name)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
