"""
LDAP models for Kerberos schema.

This module provides:
- KrbRealmContainer: Realm configuration
- KrbPrincipal: Principal entries
- KrbPwdPolicy: Password policies
- KrbTicketPolicy: Ticket policies
"""

from typing import List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class KrbRealmContainer(LDAPModel):
    """Kerberos realm container.

    Based on krb5.schema krbRealmContainer.
    STRUCTURAL object class.

    MUST: cn
    MAY: krbUPEnabled, krbLdapServers, krbSupportedEncSaltTypes,
         krbTicketPolicyReference, krbPwdPolicyReference, krbKdcServers,
         krbPwdServers, krbAdmServers
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="realmName",
        help_text="Realm name (e.g., 'EXAMPLE.COM')",
    )
    krb_up_enabled = models.BooleanField(
        default=True,
        verbose_name="krbUPEnabled",
        help_text="Whether user password is used for Kerberos auth",
    )
    krb_ldap_servers = models.JSONField(
        blank=True,
        default=list,
        verbose_name="krbLdapServers",
        help_text="List of LDAP server URIs",
    )
    krb_supported_enc_salt_types = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbSupportedEncSaltTypes",
        help_text="Supported encryption/salt type combinations",
    )
    krb_default_enc_salt_types = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbDefaultEncSaltTypes",
        help_text="Default encryption/salt type combinations",
    )
    krb_ticket_policy_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbTicketPolicyReference",
        help_text="DN of default ticket policy",
    )
    krb_pwd_policy_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbPwdPolicyReference",
        help_text="DN of default password policy",
    )
    krb_kdc_servers = models.JSONField(
        blank=True,
        default=list,
        verbose_name="krbKdcServers",
        help_text="List of KDC server DNs",
    )
    krb_pwd_servers = models.JSONField(
        blank=True,
        default=list,
        verbose_name="krbPwdServers",
        help_text="List of password server DNs",
    )
    krb_adm_servers = models.JSONField(
        blank=True,
        default=list,
        verbose_name="krbAdmServers",
        help_text="List of admin server DNs",
    )
    krb_sub_trees = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbSubTrees",
        help_text="Base DN for realm subtree",
    )
    krb_search_scope = models.PositiveIntegerField(
        default=1,
        verbose_name="krbSearchScope",
        help_text="Search scope (1=ONE, 2=SUB_TREE)",
    )

    ldap_base_dn = settings.LDAP_OU_KRB + "," + settings.LDAP_BASE_DN
    object_classes = ["krbRealmContainer"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'krb_up_enabled': 'krbUPEnabled',
        'krb_ldap_servers': 'krbLdapServers',
        'krb_supported_enc_salt_types': 'krbSupportedEncSaltTypes',
        'krb_default_enc_salt_types': 'krbDefaultEncSaltTypes',
        'krb_ticket_policy_reference': 'krbTicketPolicyReference',
        'krb_pwd_policy_reference': 'krbPwdPolicyReference',
        'krb_kdc_servers': 'krbKdcServers',
        'krb_pwd_servers': 'krbPwdServers',
        'krb_adm_servers': 'krbAdmServers',
        'krb_sub_trees': 'krbSubTrees',
        'krb_search_scope': 'krbSearchScope',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_krb_realms"
        verbose_name = "Kerberos Realm"
        verbose_name_plural = "Kerberos Realms"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this realm."""
        from ..utils.dn import build_krb_realm_dn

        return build_krb_realm_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class KrbPrincipal(LDAPModel):
    """Kerberos principal entry.

    Based on krb5.schema krbPrincipal.
    STRUCTURAL object class (auxiliary krbPrincipalAux).

    MUST: krbPrincipalName
    MAY: Various principal attributes

    Note: In practice, principals are often stored as auxiliary
    attributes on inetOrgPerson entries. This model supports both
    standalone principals and references to users.
    """

    # Principal name is required by STRUCTURAL class
    krb_principal_name = models.CharField(
        max_length=255,
        verbose_name="krbPrincipalName",
        help_text="Primary principal name (e.g., 'user@REALM.COM')",
    )
    krb_canonical_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbCanonicalName",
        help_text="Canonical principal name",
    )
    krb_principal_type = models.PositiveIntegerField(
        default=1,
        verbose_name="krbPrincipalType",
        help_text="Principal type (1=user, 2=service)",
    )

    # Status flags
    krb_up_enabled = models.BooleanField(
        default=True,
        verbose_name="krbUPEnabled",
        help_text="Whether user password is used for Kerberos auth",
    )
    krb_principal_expiration = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="krbPrincipalExpiration",
        help_text="When the principal account expires",
    )
    krb_password_expiration = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="krbPasswordExpiration",
        help_text="When the Kerberos password expires",
    )
    krb_login_failed_count = models.PositiveIntegerField(
        default=0,
        verbose_name="krbLoginFailedCount",
        help_text="Number of consecutive login failures",
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

    # Policy references
    krb_ticket_policy_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbTicketPolicyReference",
        help_text="DN of ticket policy reference",
    )
    krb_pwd_policy_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbPwdPolicyReference",
        help_text="DN of password policy reference",
    )

    # Ticket flags
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

    # Delegation and auth indicators
    krb_allowed_to_delegate_to = models.JSONField(
        blank=True,
        default=list,
        verbose_name="krbAllowedToDelegateTo",
        help_text="List of services this principal can delegate to",
    )
    krb_principal_auth_ind = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="krbPrincipalAuthInd",
        help_text="Authentication indicators for service principals",
    )

    # Realm association
    realm = models.ForeignKey(
        "KrbRealmContainer",
        on_delete=models.PROTECT,
        related_name="principals",
        help_text="Associated Kerberos realm",
    )

    ldap_base_dn = ""
    object_classes = ["krbPrincipal", "krbPrincipalAux"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'krb_principal_name': 'krbPrincipalName',
        'krb_canonical_name': 'krbCanonicalName',
        'krb_principal_type': 'krbPrincipalType',
        'krb_up_enabled': 'krbUPEnabled',
        'krb_principal_expiration': 'krbPrincipalExpiration',
        'krb_password_expiration': 'krbPasswordExpiration',
        'krb_login_failed_count': 'krbLoginFailedCount',
        'krb_last_successful_auth': 'krbLastSuccessfulAuth',
        'krb_last_failed_auth': 'krbLastFailedAuth',
        'krb_ticket_policy_reference': 'krbTicketPolicyReference',
        'krb_pwd_policy_reference': 'krbPwdPolicyReference',
        'krb_ticket_flags': 'krbTicketFlags',
        'krb_max_ticket_life': 'krbMaxTicketLife',
        'krb_max_renewable_age': 'krbMaxRenewableAge',
        'krb_allowed_to_delegate_to': 'krbAllowedToDelegateTo',
        'krb_principal_auth_ind': 'krbPrincipalAuthInd',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_krb_principals"
        verbose_name = "Kerberos Principal"
        verbose_name_plural = "Kerberos Principals"

    def __str__(self) -> str:
        return self.krb_principal_name

    @property
    def dn(self) -> str:
        """Get the DN for this principal."""
        from ..utils.dn import build_krb_principal_dn

        # Extract realm from the principal name or use the associated realm
        if "@" in self.krb_principal_name:
            realm_name = self.krb_principal_name.split("@")[1]
        else:
            realm_name = self.realm.cn if hasattr(self, "realm") and self.realm else ""

        return build_krb_principal_dn(self.krb_principal_name)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class KrbPwdPolicy(LDAPModel):
    """Kerberos password policy.

    Based on krb5.schema krbPwdPolicy.
    STRUCTURAL object class.

    MUST: cn
    MAY: Various password policy attributes
    """

    cn = models.CharField(
        max_length=255,
        help_text="Policy name",
    )
    krb_max_pwd_life = models.PositiveIntegerField(
        default=settings.KRB_DEFAULT_MAX_PWD_LIFE,
        verbose_name="krbMaxPwdLife",
        help_text="Maximum password lifetime in seconds (default 90 days)",
    )
    krb_min_pwd_life = models.PositiveIntegerField(
        default=settings.KRB_DEFAULT_MIN_PWD_LIFE,
        verbose_name="krbMinPwdLife",
        help_text="Minimum password lifetime in seconds (default 1 day)",
    )
    krb_pwd_min_length = models.PositiveIntegerField(
        default=settings.KRB_DEFAULT_PWD_MIN_LENGTH,
        verbose_name="krbPwdMinLength",
        help_text="Minimum password length (default 8)",
    )
    krb_pwd_max_failure = models.PositiveIntegerField(
        default=settings.KRB_DEFAULT_PWD_MAX_FAILURE,
        verbose_name="krbPwdMaxFailure",
        help_text="Maximum consecutive failures before lockout (default 5)",
    )
    krb_pwd_lockout_duration = models.PositiveIntegerField(
        default=settings.KRB_DEFAULT_PWD_LOCKOUT_DURATION,
        verbose_name="krbPwdLockoutDuration",
        help_text="Lockout duration in seconds (default 900/15min)",
    )
    krb_pwd_history_length = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="krbPwdHistoryLength",
        help_text="Number of previous passwords to remember",
    )
    krb_pwd_min_diff_chars = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="krbPwdMinDiffChars",
        help_text="Minimum different characters required in new password",
    )

    ldap_base_dn = settings.LDAP_OU_KRB + "," + settings.LDAP_BASE_DN
    object_classes = ["krbPwdPolicy"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'krb_max_pwd_life': 'krbMaxPwdLife',
        'krb_min_pwd_life': 'krbMinPwdLife',
        'krb_pwd_min_length': 'krbPwdMinLength',
        'krb_pwd_max_failure': 'krbPwdMaxFailure',
        'krb_pwd_lockout_duration': 'krbPwdLockoutDuration',
        'krb_pwd_history_length': 'krbPwdHistoryLength',
        'krb_pwd_min_diff_chars': 'krbPwdMinDiffChars',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_krb_password_policies"
        verbose_name = "Kerberos Password Policy"
        verbose_name_plural = "Kerberos Password Policies"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this policy."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_KRB)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class KrbTicketPolicy(LDAPModel):
    """Kerberos ticket policy.

    Based on krb5.schema krbTicketPolicy.
    STRUCTURAL object class.

    MUST: cn
    MAY: Ticket lifetime and renewable age attributes
    """

    cn = models.CharField(
        max_length=255,
        help_text="Policy name",
    )
    krb_max_ticket_life = models.PositiveIntegerField(
        default=settings.KRB_DEFAULT_TICKET_LIFETIME,
        verbose_name="krbMaxTicketLife",
        help_text="Maximum ticket lifetime in seconds (default 86400/24h)",
    )
    krb_max_renewable_age = models.PositiveIntegerField(
        default=settings.KRB_DEFAULT_RENEWABLE_AGE,
        verbose_name="krbMaxRenewableAge",
        help_text="Maximum renewable age in seconds (default 604800/7d)",
    )
    krb_ticket_flags = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="krbTicketFlags",
        help_text="Default ticket flags for this policy",
    )

    ldap_base_dn = settings.LDAP_OU_KRB + "," + settings.LDAP_BASE_DN
    object_classes = ["krbTicketPolicy"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'krb_max_ticket_life': 'krbMaxTicketLife',
        'krb_max_renewable_age': 'krbMaxRenewableAge',
        'krb_ticket_flags': 'krbTicketFlags',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_krb_ticket_policies"
        verbose_name = "Kerberos Ticket Policy"
        verbose_name_plural = "Kerberos Ticket Policies"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this policy."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_KRB)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
