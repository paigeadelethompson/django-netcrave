"""
LDAP models for NIS schema attributes.

This module provides:
- PosixAccount: POSIX account with shadow support
- PosixGroup: POSIX group model
- ShadowAccount: Shadow password attributes (in domains.py)
- NisObject: General NIS map object model
- ipService, ipProtocol, oncRpc: Network services
- ipHost: IP host addressing
- ipNetwork: IP network
- nisNetgroup: NIS netgroups
- ieee802Device: IEEE 802 device (MAC address)
- bootableDevice: Bootable device
"""

from typing import Dict, List

from django.conf import settings
from django.db import models

from .base import LDAPModel


class PosixAccount(LDAPModel):
    """POSIX account model.

    Based on posixAccount from nis.schema.
    AUXILIARY object class.

    MUST: cn, uid, uidNumber, gidNumber, homeDirectory
    MAY: userPassword, loginShell, gecos, description
    """

    # Core POSIX attributes
    cn = models.CharField(
        max_length=255,
        help_text="Common name",
    )
    uid = models.CharField(
        max_length=255,
        unique=True,
        help_text="User ID (uid)",
    )
    uid_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="uidNumber",
        help_text="Unix UID (auto-increment if not set)",
    )
    gid_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=100,
        verbose_name="gidNumber",
        help_text="Unix GID (primary group ID)",
    )
    home_directory = models.CharField(
        max_length=255,
        default="/home",
        verbose_name="homeDirectory",
        help_text="Home directory path",
    )

    # Optional POSIX attributes
    user_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="userPassword",
        help_text="User password hash",
    )
    login_shell = models.CharField(
        max_length=255,
        default="/bin/bash",
        verbose_name="loginShell",
        help_text="Path to user's login shell",
    )
    gecos = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="GECOS field (user information)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this account",
    )

    ldap_base_dn = settings.LDAP_OU_USERS + "," + settings.LDAP_BASE_DN
    object_classes = ["posixAccount"]

    objects = models.Manager()

    class Meta:
        db_table = "ldap_posix_accounts"
        verbose_name = "POSIX Account"
        verbose_name_plural = "POSIX Accounts"

    def __str__(self) -> str:
        return self.uid

    @property
    def dn(self) -> str:
        """Get the DN for this account."""
        from ..utils.dn import build_user_dn

        return build_user_dn(self.uid)

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()

    def save(self, *args, **kwargs):
        """Auto-generate UID number if not set."""
        from .base import LDAPCounter

        if self.uid_number is None:
            counter, _ = LDAPCounter.objects.get_or_create(
                key=LDAPCounter.UID_COUNTER_KEY,
                defaults={"value": settings.LDAP_DEFAULT_UID_NUMBER},
            )
            self.uid_number = counter.value
            counter.value += 1
            counter.save(update_fields=["value"])

        super().save(*args, **kwargs)


class NisPosixGroup(LDAPModel):
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
        verbose_name="gidNumber",
        help_text="Unix GID (auto-increment if not set)",
    )
    member_uid = models.JSONField(
        blank=True,
        default=list,
        verbose_name="memberUid",
        help_text="List of member UIDs (usernames)",
    )
    user_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="userPassword",
        help_text="Group password hash",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Group description",
    )

    ldap_base_dn = settings.LDAP_OU_GROUPS + "," + settings.LDAP_BASE_DN
    object_classes = ["posixGroup"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'gid_number': 'gidNumber',
        'member_uid': 'memberUid',
        'user_password': 'userPassword',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_nis_posix_groups"
        verbose_name = "NIS POSIX Group"
        verbose_name_plural = "NIS POSIX Groups"

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
        from .base import LDAPCounter

        if self.gid_number is None:
            counter, _ = LDAPCounter.objects.get_or_create(
                key=LDAPCounter.GID_COUNTER_KEY,
                defaults={"value": settings.LDAP_DEFAULT_GID_NUMBER},
            )
            self.gid_number = counter.value
            counter.value += 1
            counter.save(update_fields=["value"])

        super().save(*args, **kwargs)


class NisObject(LDAPModel):
    """NIS map object model.

    Based on nisObject from nis.schema.
    STRUCTURAL object class.

    MUST: cn, nisMapName, nisMapEntry
    MAY: description
    """

    cn = models.CharField(
        max_length=255,
        help_text="Common name (key for the map entry)",
    )
    nis_map_name = models.CharField(
        max_length=255,
        verbose_name="nisMapName",
        help_text="Name of the NIS map this entry belongs to",
    )
    nis_map_entry = models.TextField(
        verbose_name="nisMapEntry",
        help_text="Value of the map entry (left=value format)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this map entry",
    )

    ldap_base_dn = settings.LDAP_OU_GROUPS + "," + settings.LDAP_BASE_DN
    object_classes = ["nisObject"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'nis_map_name': 'nisMapName',
        'nis_map_entry': 'nisMapEntry',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_nis_objects"
        verbose_name = "NIS Object"
        verbose_name_plural = "NIS Objects"

    def __str__(self) -> str:
        return f"{self.cn} in {self.nis_map_name}"

    @property
    def dn(self) -> str:
        """Get the DN for this NIS object."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_GROUPS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class IpService(LDAPModel):
    """IP service model.

    Based on ipService from nis.schema.
    STRUCTURAL object class.

    MUST: cn, ipServicePort, ipServiceProtocol
    MAY: description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="serviceName",
        help_text="Service name (cn)",
    )
    ip_service_port = models.PositiveIntegerField(
        verbose_name="ipServicePort",
        help_text="IP port number",
    )
    ip_service_protocol = models.CharField(
        max_length=20,
        verbose_name="ipServiceProtocol",
        help_text="Protocol (tcp, udp, etc.)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this service",
    )

    ldap_base_dn = settings.LDAP_OU_NIS + "," + settings.LDAP_BASE_DN
    object_classes = ["ipService"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'ip_service_port': 'ipServicePort',
        'ip_service_protocol': 'ipServiceProtocol',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_ip_services"
        verbose_name = "IP Service"
        verbose_name_plural = "IP Services"

    def __str__(self) -> str:
        return f"{self.cn}/{self.ip_service_protocol}:{self.ip_service_port}"

    @property
    def dn(self) -> str:
        """Get the DN for this service."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_NIS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class IpProtocol(LDAPModel):
    """IP protocol model.

    Based on ipProtocol from nis.schema.
    STRUCTURAL object class.

    MUST: cn, ipProtocolNumber
    MAY: description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="protocolName",
        help_text="Protocol name (cn)",
    )
    ip_protocol_number = models.PositiveIntegerField(
        verbose_name="ipProtocolNumber",
        help_text="IP protocol number (e.g., 6 for TCP, 17 for UDP)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this protocol",
    )

    ldap_base_dn = settings.LDAP_OU_NIS + "," + settings.LDAP_BASE_DN
    object_classes = ["ipProtocol"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'ip_protocol_number': 'ipProtocolNumber',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_ip_protocols"
        verbose_name = "IP Protocol"
        verbose_name_plural = "IP Protocols"

    def __str__(self) -> str:
        return f"{self.cn} (number {self.ip_protocol_number})"

    @property
    def dn(self) -> str:
        """Get the DN for this protocol."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_NIS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class OncRpc(LDAPModel):
    """ONC/RPC model.

    Based on oncRpc from nis.schema.
    STRUCTURAL object class.

    MUST: cn, oncRpcNumber
    MAY: description
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="rpcName",
        help_text="RPC program name (cn)",
    )
    onc_rpc_number = models.PositiveIntegerField(
        verbose_name="oncRpcNumber",
        help_text="ONC/RPC program number",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this RPC service",
    )

    ldap_base_dn = settings.LDAP_OU_NIS + "," + settings.LDAP_BASE_DN
    object_classes = ["oncRpc"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'onc_rpc_number': 'oncRpcNumber',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_onc_rpc"
        verbose_name = "ONC/RPC Service"
        verbose_name_plural = "ONC/RPC Services"

    def __str__(self) -> str:
        return f"{self.cn} (number {self.onc_rpc_number})"

    @property
    def dn(self) -> str:
        """Get the DN for this RPC service."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_NIS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class IpHost(LDAPModel):
    """IP host model.

    Based on ipHost from nis.schema.
    AUXILIARY object class.

    MUST: cn, ipHostNumber
    MAY: l, description, manager
    """

    # Base model for ipHost - used as mixin or standalone
    cn = models.CharField(
        max_length=255,
        verbose_name="hostName",
        help_text="Host name (cn)",
    )
    ip_host_number = models.JSONField(
        default=list,
        verbose_name="ipHostNumber",
        help_text="List of IP addresses",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this host",
    )
    manager = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Manager DN",
    )

    ldap_base_dn = settings.LDAP_OU_HOSTS + "," + settings.LDAP_BASE_DN
    object_classes = ["ipHost"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'ip_host_number': 'ipHostNumber',
        'description': 'description',
        'manager': 'manager',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_ip_hosts"
        verbose_name = "IP Host"
        verbose_name_plural = "IP Hosts"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this host."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_HOSTS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class IpNetwork(LDAPModel):
    """IP network model.

    Based on ipNetwork from nis.schema.
    STRUCTURAL object class.

    MUST: cn, ipNetworkNumber
    MAY: ipNetmaskNumber, l, description, manager
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="networkName",
        help_text="Network name (cn)",
    )
    ip_network_number = models.CharField(
        max_length=50,
        verbose_name="ipNetworkNumber",
        help_text="Network address",
    )
    ip_netmask_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="ipNetmaskNumber",
        help_text="Network netmask",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this network",
    )
    manager = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Manager DN",
    )

    ldap_base_dn = settings.LDAP_OU_NIS + "," + settings.LDAP_BASE_DN
    object_classes = ["ipNetwork"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'ip_network_number': 'ipNetworkNumber',
        'ip_netmask_number': 'ipNetmaskNumber',
        'description': 'description',
        'manager': 'manager',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_ip_networks"
        verbose_name = "IP Network"
        verbose_name_plural = "IP Networks"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this network."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_NIS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class NisNetgroup(LDAPModel):
    """NIS netgroup model.

    Based on nisNetgroup from nis.schema.
    STRUCTURAL object class.

    MUST: cn
    MAY: nisNetgroupTriple, memberNisNetgroup, description
    """

    cn = models.CharField(
        max_length=255,
        help_text="Netgroup name (cn)",
    )
    nis_netgroup_triple = models.JSONField(
        blank=True,
        default=list,
        verbose_name="nisNetgroupTriple",
        help_text="List of netgroup triples [(host,user,domain), ...]",
    )
    member_nis_netgroup = models.JSONField(
        blank=True,
        default=list,
        verbose_name="memberNisNetgroup",
        help_text="List of member netgroups",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of this netgroup",
    )

    ldap_base_dn = settings.LDAP_OU_NETGROUPS + "," + settings.LDAP_BASE_DN
    object_classes = ["nisNetgroup"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'nis_netgroup_triple': 'nisNetgroupTriple',
        'member_nis_netgroup': 'memberNisNetgroup',
        'description': 'description',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_nis_netgroups"
        verbose_name = "NIS Netgroup"
        verbose_name_plural = "NIS Netgroups"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this netgroup."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_NETGROUPS)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class Ieee802Device(LDAPModel):
    """IEEE 802 device model (MAC address).

    Based on ieee802Device from nis.schema.
    AUXILIARY object class.

    MAY: macAddress
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="deviceName",
        help_text="Device name (cn)",
    )
    mac_address = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name="macAddress",
        help_text="MAC address (format: AA:BB:CC:DD:EE:FF)",
    )

    ldap_base_dn = settings.LDAP_OU_DEVICES + "," + settings.LDAP_BASE_DN
    object_classes = ["ieee802Device"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'mac_address': 'macAddress',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_ieee802_devices"
        verbose_name = "IEEE 802 Device"
        verbose_name_plural = "IEEE 802 Devices"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this device."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_DEVICES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()


class BootableDevice(LDAPModel):
    """Bootable device model.

    Based on bootableDevice from nis.schema.
    AUXILIARY object class.

    MAY: bootFile, bootParameter
    """

    cn = models.CharField(
        max_length=255,
        verbose_name="deviceName",
        help_text="Device name (cn)",
    )
    boot_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="bootFile",
        help_text="Boot image filename",
    )
    boot_parameter = models.TextField(
        blank=True,
        null=True,
        verbose_name="bootParameter",
        help_text="Boot parameters",
    )

    ldap_base_dn = settings.LDAP_OU_DEVICES + "," + settings.LDAP_BASE_DN
    object_classes = ["bootableDevice"]

    ldap_attributes_map: Dict[str, str] = {
        'cn': 'cn',
        'boot_file': 'bootFile',
        'boot_parameter': 'bootParameter',
    }

    objects = models.Manager()

    class Meta:
        db_table = "ldap_bootable_devices"
        verbose_name = "Bootable Device"
        verbose_name_plural = "Bootable Devices"

    def __str__(self) -> str:
        return self.cn

    @property
    def dn(self) -> str:
        """Get the DN for this device."""
        from ..utils.dn import build_ou

        base = build_ou(settings.LDAP_OU_DEVICES)
        return f"cn={self.cn},{base}"

    @classmethod
    def get_object_classes(cls) -> List[str]:
        """Get object classes for this model."""
        return cls.object_classes.copy()
