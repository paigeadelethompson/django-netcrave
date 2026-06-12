"""
LDAP models for domains (users and groups).

This module provides:
- PosixAccountMixin: Shared attributes for POSIX-enabled accounts
- InetOrgPerson: Primary user model with inetOrgPerson, posixAccount, kerberos, radius support
- PosixGroup: POSIX group model
- GroupOfNames: General group model with DN-based membership
"""

from typing import List, Optional

from django.conf import settings
from django.db import models

from .base import LDAPCounter, LDAPManager, LDAPModel
from netcrave_settings.utils import defaults


class PosixAccountMixin(models.Model):
    """Mixin for POSIX account attributes.

    Based on posixAccount from nis.schema.
    MUST: cn, uid, uidNumber, gidNumber, homeDirectory
    MAY: userPassword, loginShell, gecos, description
    """

    # Core POSIX attributes
    uid_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Unix UID (auto-increment if not set)",
    )
    gid_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=defaults.get_default_gid_number,
        help_text="Unix GID (primary group ID)",
    )
    login_shell = models.CharField(
        max_length=255,
        default=defaults.get_default_login_shell,
        help_text="Path to user's login shell",
    )
    gecos = models.CharField(
        max_length=255,
        default=defaults.get_default_gecos,
        help_text="GECOS field (user information)",
    )

    # Shadow password attributes
    shadow_last_change = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Days since Jan 1, 1970 password was last changed",
    )
    shadow_min = models.IntegerField(
        default=0,
        help_text="Minimum days between password changes",
    )
    shadow_max = models.IntegerField(
        default=99999,
        help_text="Maximum days between password changes",
    )
    shadow_warning = models.IntegerField(
        default=7,
        help_text="Days before password expires to warn user",
    )
    shadow_inactive = models.IntegerField(
        default=-1,
        help_text="Days after password expires until account is disabled",
    )
    shadow_expire = models.IntegerField(
        default=-1,
        help_text="Days since Jan 1, 1970 when account expires",
    )
    shadow_flag = models.PositiveIntegerField(
        default=0,
        help_text="Reserved for future use (always 0)",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Auto-generate IDs if not set."""
        # Auto-increment UID number
        if self.uid_number is None:
            self.uid_number = LDAPCounter.objects.get_next_uid_number()

        # Set default shadow dates if not set
        if self.shadow_last_change is None:
            from datetime import date

            self.shadow_last_change = (
                date.today().toordinal() - date(1970, 1, 1).toordinal()
            )

        super().save(*args, **kwargs)


class InetOrgPerson(LDAPModel):
    """Primary user model combining inetOrgPerson with auxiliary classes.

    Object Classes:
    - inetOrgPerson (structural): Core user information
    - posixAccount (auxiliary): Unix/Linux account attributes
    - krbPrincipalAux (auxiliary): Kerberos authentication
    - radiusprofile (auxiliary): RADIUS profile

    MUST (inetOrgPerson):
        cn, sn (surname)

    MAY include:
        uid, mail, givenName, displayName, title, ou,
        telephoneNumber, mobile, homePhone,pager, facsimileTelephoneNumber,
        employeeNumber, employeeType, departmentNumber
    """

    # Basic identity attributes
    uid = models.CharField(
        max_length=255,
        unique=True,
        help_text="User login ID (uid)",
    )
    cn = models.CharField(
        max_length=255,
        help_text="Common name",
    )
    sn = models.CharField(
        max_length=255,
        help_text="Surname (last name)",
    )
    given_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="givenName",
        help_text="Given name (first name)",
    )
    display_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Display name for UI purposes",
    )
    mail = models.EmailField(
        blank=True,
        null=True,
        help_text="Email address",
    )

    # Organization attributes
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Job title (RFC2798: inetOrgPerson)",
    )
    ou = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalUnit",
        help_text="Organizational unit",
    )
    department_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="departmentNumber",
        help_text="Department identifier",
    )
    employee_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="employeeNumber",
        help_text="Employee identifier",
    )
    employee_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="employeeType",
        help_text="Employment type (Contractor, Employee, etc.)",
    )

    # Contact attributes
    telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="telephoneNumber",
        help_text="Work phone number",
    )
    mobile = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Mobile/cellular phone number",
    )
    home_phone = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="homePhone",
        help_text="Home phone number",
    )
    pager = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Pager number",
    )
    facsimile_telephone_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="facsimileTelephoneNumber",
        help_text="Fax number",
    )

    # POSIX attributes
    uid_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Unix UID (auto-increment if not set)",
    )
    gid_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=defaults.get_default_gid_number,
        help_text="Unix GID (primary group ID)",
    )
    login_shell = models.CharField(
        max_length=255,
        default=defaults.get_default_login_shell,
        verbose_name="loginShell",
        help_text="Path to user's login shell",
    )
    gecos = models.CharField(
        max_length=255,
        default=defaults.get_default_gecos,
        help_text="GECOS field (user information)",
    )
    home_directory = models.CharField(
        max_length=255,
        default="/home",
        verbose_name="homeDirectory",
        help_text="Home directory path",
    )

    # Shadow password attributes
    shadow_last_change = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Days since Jan 1, 1970 password was last changed",
    )
    shadow_min = models.IntegerField(default=0)
    shadow_max = models.IntegerField(default=99999)
    shadow_warning = models.IntegerField(default=7)
    shadow_inactive = models.IntegerField(default=-1)
    shadow_expire = models.IntegerField(default=-1)
    shadow_flag = models.PositiveIntegerField(default=0)

    # Kerberos attributes
    krb_principal_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbPrincipalName",
        help_text="Kerberos principal name (e.g., user@REALM.COM)",
    )
    krb_canonical_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbCanonicalName",
        help_text="Canonical Kerberos principal name",
    )
    krb_password_expiration = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="krbPasswordExpiration",
        help_text="When the Kerberos password expires",
    )
    krb_principal_expiration = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="krbPrincipalExpiration",
        help_text="When the principal account expires",
    )
    krb_pwd_policy_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbPwdPolicyReference",
        help_text="DN of password policy reference",
    )
    krb_ticket_policy_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbTicketPolicyReference",
        help_text="DN of ticket policy reference",
    )
    krb_up_enabled = models.BooleanField(
        default=True,
        verbose_name="krbUPEnabled",
        help_text="Whether user password is used for Kerberos auth",
    )
    krb_last_successful_auth = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="krbLastSuccessfulAuth",
        help_text="Last successful authentication time",
    )
    krb_last_failed_auth = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="krbLastFailedAuth",
        help_text="Last failed authentication time",
    )
    krb_login_failed_count = models.PositiveIntegerField(
        default=0,
        verbose_name="krbLoginFailedCount",
        help_text="Number of consecutive login failures",
    )

    # RADIUS attributes
    radius_auth_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="radiusAuthType",
        help_text="RADIUS authentication type (PAP, CHAP, MSCHAPV2)",
    )
    radius_framed_ip_address = models.GenericIPAddressField(
        protocol="IPv4",
        blank=True,
        null=True,
        verbose_name="radiusFramedIPAddress",
        help_text="Static IP address for RADIUS user",
    )
    radius_service_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="radiusServiceType",
        help_text="RADIUS service type (Framed-User, etc.)",
    )
    radius_session_timeout = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="radiusSessionTimeout",
        help_text="Session timeout in seconds",
    )
    radius_idle_timeout = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="radiusIdleTimeout",
        help_text="Idle timeout in seconds",
    )
    radius_simultaneous_use = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=1,
        verbose_name="radiusSimultaneousUse",
        help_text="Maximum simultaneous sessions",
    )

    # Additional Kerberos attributes
    krb_ticket_flags = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="krbTicketFlags",
        help_text="Kerberos ticket flags (bit mask)",
    )
    krb_max_ticket_life = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="krbMaxTicketLife",
        help_text="Maximum ticket lifetime in seconds",
    )
    krb_max_renewable_age = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="krbMaxRenewableAge",
        help_text="Maximum renewable age in seconds",
    )

    ldap_base_dn = settings.LDAP_OU_USERS + "," + settings.LDAP_BASE_DN
    object_classes = [
        "inetOrgPerson",
        "posixAccount",
        "krbPrincipalAux",
        "radiusprofile",
    ]

    objects = LDAPManager()

    class Meta:
        db_table = "ldap_users"
        verbose_name = "User (inetOrgPerson)"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.cn or self.uid

    @property
    def dn(self) -> str:
        """Get the DN for this user."""
        from ..utils.dn import build_user_dn

        return build_user_dn(self.uid)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def save(self, *args, **kwargs):
        """Auto-generate attributes on save."""
        # Auto-increment UID number if not set
        if self.uid_number is None:
            self.uid_number = LDAPCounter.objects.get_next_uid_number()

        # Set default shadow dates if not set
        if self.shadow_last_change is None:
            from datetime import date

            self.shadow_last_change = (
                date.today().toordinal() - date(1970, 1, 1).toordinal()
            )

        # Set default Kerberos password expiration (90 days from now)
        if (
            self.krb_password_expiration is None
            and settings.KRB_DEFAULT_MAX_PWD_LIFE
        ):
            from datetime import timedelta

            self.krb_password_expiration = (
                defaults.get_default_shadow_dates()["shadow_last_change"]
                + timedelta(days=settings.KRB_DEFAULT_MAX_PWD_LIFE / 86400)
            )

        super().save(*args, **kwargs)


class PosixGroup(LDAPModel):
    """POSIX group model.

    Based on posixGroup from nis.schema.
    STRUCTURAL object class.

    MUST: cn, gidNumber
    MAY: userPassword, memberUid, description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="groupName",
        help_text="Group name (cn)",
    )
    gid_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Unix GID (auto-increment if not set)",
    )
    member_uid = models.JSONField(
        blank=True,
        default=list,
        verbose_name="memberUid",
        help_text="List of member UIDs (usernames)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Group description",
    )

    ldap_base_dn = settings.LDAP_OU_GROUPS + "," + settings.LDAP_BASE_DN
    object_classes = ["posixGroup"]

    objects = LDAPManager()

    class Meta:
        db_table = "ldap_posix_groups"
        verbose_name = "POSIX Group"
        verbose_name_plural = "POSIX Groups"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this group."""
        from ..utils.dn import build_group_dn

        return build_group_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def save(self, *args, **kwargs):
        """Auto-generate GID number if not set."""
        if self.gid_number is None:
            self.gid_number = LDAPCounter.objects.get_next_gid_number()
        super().save(*args, **kwargs)


class GroupOfNames(LDAPModel):
    """General group model with DN-based membership.

    Based on groupOfNames from core.schema.
    STRUCTURAL object class.

    MUST: cn, member
    MAY: businessCategory, seeAlso, owner, ou, o, description, userPassword
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="groupName",
        help_text="Group name (cn)",
    )
    members = models.JSONField(
        blank=True,
        default=list,
        help_text="List of member DNs",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Group description",
    )
    ou = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organizationalUnit",
        help_text="Organizational unit",
    )
    o = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="organization",
        help_text="Organization name",
    )

    ldap_base_dn = settings.LDAP_OU_GROUPS + "," + settings.LDAP_BASE_DN
    object_classes = ["groupOfNames"]

    objects = LDAPManager()

    class Meta:
        db_table = "ldap_group_of_names"
        verbose_name = "Group of Names"
        verbose_name_plural = "Groups of Names"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this group."""
        from ..utils.dn import build_group_dn

        return build_group_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
