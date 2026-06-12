"""
LDAP models for Asterisk schema.

This module provides:
- AsteriskExtension: Base dialplan entry
- AsteriskIAXUser: IAX endpoint
- AsteriskSIPUser: SIP endpoint
- AsteriskVoiceMail: Voicemail entries
- AsteriskConfig: Configuration entries
"""

from typing import List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class AsteriskExtension(LDAPModel):
    """Base Asterisk dialplan extension.

    Based on asterisk.schema AsteriskExtension.
    AUXILIARY object class.

    MUST: cn
    MAY: AstContext, AstExtension, AstPriority,
         AstApplication, AstApplicationData
    """

    cn = models.CharField(
        max_length=255,
        help_text="Extension name/identifier",
    )
    ast_context = models.CharField(
        max_length=100,
        default=settings.ASTERISK_DEFAULT_CONTEXT,
        verbose_name="AstContext",
        help_text="Asterisk context (e.g., 'default', 'internal')",
    )
    ast_extension = models.CharField(
        max_length=50,
        verbose_name="AstExtension",
        help_text="Extension number (e.g., '100', '5551234')",
    )
    ast_priority = models.PositiveIntegerField(
        default=settings.ASTERISK_DEFAULT_PRIORITY,
        verbose_name="AstPriority",
        help_text="Priority within the context (execution order)",
    )
    ast_application = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstApplication",
        help_text="Asterisk application to execute (e.g., 'Dial', 'VoiceMail')",
    )
    ast_application_data = models.TextField(
        blank=True,
        null=True,
        verbose_name="AstApplicationData",
        help_text="Application parameters (e.g., 'SIP/100', 'mailbox')",
    )

    ldap_base_dn = settings.LDAP_OU_AST + "," + settings.LDAP_BASE_DN
    object_classes = ["AsteriskExtension"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_asterisk_extensions"
        verbose_name = "Asterisk Extension"
        verbose_name_plural = "Asterisk Extensions"

    def __str__(self) -> str:
        return f"{self.ast_context}/{self.ast_extension}"

    @property
    def dn(self) -> str:
        """Get the DN for this extension."""
        from ..utils.dn import build_asterisk_dn

        return build_asterisk_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class AsteriskIAXUser(LDAPModel):
    """IAX2 User endpoint.

    Based on asterisk.schema AsteriskIAXUser.
    AUXILIARY object class (extends AsteriskExtension).

    MUST: cn
    MAY: Various IAX-specific attributes
    """

    # Extension reference
    cn = models.CharField(
        max_length=255,
        help_text="Account name/identifier",
    )
    ast_context = models.CharField(
        max_length=100,
        default=settings.ASTERISK_DEFAULT_CONTEXT,
        verbose_name="AstContext",
    )
    ast_extension = models.CharField(
        max_length=50,
        verbose_name="AstExtension",
    )
    ast_priority = models.PositiveIntegerField(
        default=settings.ASTERISK_DEFAULT_PRIORITY,
        verbose_name="AstPriority",
    )
    ast_application = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstApplication",
    )
    ast_application_data = models.TextField(
        blank=True,
        null=True,
        verbose_name="AstApplicationData",
    )

    # IAX Account attributes
    ast_account_name = models.CharField(
        max_length=100,
        verbose_name="AstAccountName",
        help_text="IAX account username",
    )
    ast_md5_secret = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="AstMD5secret",
        help_text="MD5 hash of the IAX secret",
    )
    ast_account_host = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstAccountHost",
        help_text="Host address for this account",
    )
    ast_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=4569,
        verbose_name="AstPort",
        help_text="IAX port (default 4569)",
    )
    ast_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstUsername",
        help_text="Authentication username",
    )
    ast_auth_type = models.CharField(
        max_length=20,
        default="md5",
        verbose_name="AstAuthType",
        help_text="Authentication type (md5, clearpass, rsa)",
    )
    ast_account_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="AstAccountType",
        help_text="Account type (friend, peer, user)",
    )
    ast_account_caller_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstAccountCallerID",
        help_text="Caller ID for outgoing calls",
    )
    ast_account_disallowed_codec = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstAccountDisallowedCodec",
        help_text="Codecs to disallow (comma-separated)",
    )
    ast_account_allowed_codec = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstAccountAllowedCodec",
        help_text="Codecs to allow (comma-separated)",
    )

    # Network attributes
    ast_account_transport = models.CharField(
        max_length=10,
        default=settings.ASTERISK_DEFAULT_TRANSPORT,
        verbose_name="AstAccountTransport",
        help_text="Transport protocol (udp, tcp)",
    )
    ast_account_nat = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="AstAccountNAT",
        help_text="NAT handling strategy",
    )

    ldap_base_dn = settings.LDAP_OU_AST + "," + settings.LDAP_BASE_DN
    object_classes = ["AsteriskExtension", "AsteriskIAXUser"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_asterisk_iax_users"
        verbose_name = "Asterisk IAX User"
        verbose_name_plural = "Asterisk IAX Users"

    def __str__(self) -> str:
        return self.ast_account_name or self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this IAX user."""
        from ..utils.dn import build_asterisk_dn

        return build_asterisk_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class AsteriskSIPUser(LDAPModel):
    """SIP User endpoint.

    Based on asterisk.schema AsteriskSIPUser.
    AUXILIARY object class (extends AsteriskExtension).

    MUST: cn
    MAY: Various SIP-specific attributes
    """

    # Extension reference
    cn = models.CharField(
        max_length=255,
        help_text="Account name/identifier",
    )
    ast_context = models.CharField(
        max_length=100,
        default=settings.ASTERISK_DEFAULT_CONTEXT,
        verbose_name="AstContext",
    )
    ast_extension = models.CharField(
        max_length=50,
        verbose_name="AstExtension",
    )
    ast_priority = models.PositiveIntegerField(
        default=settings.ASTERISK_DEFAULT_PRIORITY,
        verbose_name="AstPriority",
    )
    ast_application = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstApplication",
    )
    ast_application_data = models.TextField(
        blank=True,
        null=True,
        verbose_name="AstApplicationData",
    )

    # SIP Account attributes
    ast_account_name = models.CharField(
        max_length=100,
        verbose_name="AstAccountName",
        help_text="SIP account username",
    )
    ast_account_secret = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="AstAccountSecret",
        help_text="SIP secret/password",
    )
    ast_account_nat = models.CharField(
        max_length=50,
        default="force_rport,comedia",
        verbose_name="AstAccountNAT",
        help_text="NAT handling strategy",
    )
    ast_account_transport = models.CharField(
        max_length=10,
        default=settings.ASTERISK_DEFAULT_TRANSPORT,
        verbose_name="AstAccountTransport",
        help_text="Transport protocol (udp, tcp, tls)",
    )
    ast_account_call_limit = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="AstAccountCallLimit",
        help_text="Maximum simultaneous calls",
    )

    # Codec settings
    ast_codecs = models.JSONField(
        blank=True,
        default=list,
        help_text="List of allowed codecs with priorities",
    )
    ast_allow = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="AstAllow",
        help_text="Allowed codecs (comma-separated)",
    )
    ast_direct_media = models.BooleanField(
        default=False,
        verbose_name="AstDirectMedia",
        help_text="Enable direct media (bypass Asterisk for media)",
    )
    ast_account_video_support = models.BooleanField(
        default=False,
        verbose_name="AstAccountVideoSupport",
        help_text="Enable video support",
    )
    ast_account_language = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="AstAccountLanguage",
        help_text="Default language (e.g., 'en', 'fr')",
    )

    # Additional SIP attributes
    ast_transport = models.CharField(
        max_length=10,
        default=settings.ASTERISK_DEFAULT_TRANSPORT,
        verbose_name="Transport",
    )
    ast_allow_overlap = models.BooleanField(
        default=False,
        verbose_name="Allow Overlap Dialing",
    )
    ast_account_disallowed_codec = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Disallowed Codec",
    )
    ast_account_allowed_codec = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Allowed Codec",
    )
    ast_account_call_group = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Call Group",
    )
    ast_account_pickup_group = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Pickup Group",
    )
    ast_account_music_on_hold = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Music On Hold Class",
    )
    ast_account_can_call_forward = models.BooleanField(
        default=True,
        verbose_name="Can Call Forward",
    )

    ldap_base_dn = settings.LDAP_OU_AST + "," + settings.LDAP_BASE_DN
    object_classes = ["AsteriskExtension", "AsteriskSIPUser"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_asterisk_sip_users"
        verbose_name = "Asterisk SIP User"
        verbose_name_plural = "Asterisk SIP Users"

    def __str__(self) -> str:
        return self.ast_account_name or self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this SIP user."""
        from ..utils.dn import build_asterisk_dn

        return build_asterisk_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class AsteriskVoiceMail(LDAPModel):
    """Voicemail entry.

    Based on asterisk.schema AsteriskVoiceMail.
    AUXILIARY object class.

    MUST: cn, AstContext, AstVoicemailMailbox, AstVoicemailPassword
    MAY: AstVoicemailFullname, AstVoicemailEmail, AstVoicemailPager,
         AstVoicemailOptions, AstVoicemailTimestamp, AstVoicemailContext
    """

    cn = models.CharField(
        max_length=255,
        help_text="Voicemail identifier",
    )
    ast_context = models.CharField(
        max_length=100,
        default=settings.ASTERISK_DEFAULT_CONTEXT,
        verbose_name="AstContext",
    )
    ast_voicemail_mailbox = models.CharField(
        max_length=50,
        verbose_name="AstVoicemailMailbox",
        help_text="Mailbox number (e.g., '1234')",
    )
    ast_voicemail_password = models.CharField(
        max_length=50,
        verbose_name="AstVoicemailPassword",
        help_text=" voicemail access code",
    )
    ast_voicemail_fullname = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstVoicemailFullname",
        help_text="User's full name for voicemail prompts",
    )
    ast_voicemail_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="AstVoicemailEmail",
        help_text="Email address for voicemail notifications",
    )
    ast_voicemail_pager = models.EmailField(
        blank=True,
        null=True,
        verbose_name="AstVoicemailPager",
        help_text="Pager/email for urgent notifications",
    )
    ast_voicemail_options = models.TextField(
        blank=True,
        null=True,
        verbose_name="AstVoicemailOptions",
        help_text="Additional voicemail options (e.g., 'attach=yes')",
    )
    ast_voicemail_context = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstVoicemailContext",
        help_text="Context for voicemail main menu",
    )

    ldap_base_dn = settings.LDAP_OU_AST + "," + settings.LDAP_BASE_DN
    object_classes = ["AsteriskExtension", "AsteriskVoiceMail"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_asterisk_voicemail"
        verbose_name = "Asterisk Voicemail"
        verbose_name_plural = "Asterisk Voicemails"

    def __str__(self) -> str:
        return f"VM {self.ast_voicemail_mailbox}"

    @property
    def dn(self) -> str:
        """Get the DN for this voicemail."""
        from ..utils.dn import build_asterisk_dn

        return build_asterisk_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class AsteriskConfig(LDAPModel):
    """Asterisk configuration entry.

    Based on asterisk.schema AsteriskConfig.
    AUXILIARY object class.

    MUST: cn
    MAY: AstConfigFilename, AstConfigCategory,
         AstConfigVariableName, AstConfigVariableValue
    """

    cn = models.CharField(
        max_length=255,
        help_text="Configuration entry identifier",
    )
    ast_config_filename = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstConfigFilename",
        help_text="Target configuration file (e.g., 'sip.conf', 'extensions.conf')",
    )
    ast_config_category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstConfigCategory",
        help_text="Configuration category/section name",
    )
    ast_config_variable_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="AstConfigVariableName",
        help_text="Configuration variable name",
    )
    ast_config_variable_value = models.TextField(
        blank=True,
        null=True,
        verbose_name="AstConfigVariableValue",
        help_text="Configuration value",
    )
    ast_config_commented = models.BooleanField(
        default=False,
        verbose_name="AstConfigCommented",
        help_text="Whether this entry is commented out",
    )

    ldap_base_dn = settings.LDAP_OU_AST + "," + settings.LDAP_BASE_DN
    object_classes = ["AsteriskExtension", "AsteriskConfig"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_asterisk_config"
        verbose_name = "Asterisk Config"
        verbose_name_plural = "Asterisk Configurations"

    def __str__(self) -> str:
        return f"{self.ast_config_filename}/{self.ast_config_category}"

    @property
    def dn(self) -> str:
        """Get the DN for this config entry."""
        from ..utils.dn import build_asterisk_dn

        return build_asterisk_dn(self.cn)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
