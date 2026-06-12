"""
LDAP Distinguished Name (DN) construction utilities.
"""

from typing import Optional

from django.conf import settings


def build_ou(ou_name: str, base_dn: Optional[str] = None) -> str:
    """Build an organizational unit DN.

    Args:
        ou_name: The OU name (e.g., 'users', 'groups')
        base_dn: Base DN to use. Defaults to settings.LDAP_BASE_DN

    Returns:
        Full DNS string (e.g., 'ou=users,dc=example,dc=com')
    """
    if base_dn is None:
        base_dn = settings.LDAP_BASE_DN
    return f"{ou_name},{base_dn}"


def build_user_dn(uid: str, ou: Optional[str] = None) -> str:
    """Build a user DN.

    Args:
        uid: The user's UID
        ou: OU to use. Defaults to settings.LDAP_OU_USERS

    Returns:
        Full DN string (e.g., 'uid=jdoe,ou=users,dc=example,dc=com')
    """
    if ou is None:
        ou = settings.LDAP_OU_USERS
    return f"uid={uid},{build_ou(ou)}"


def build_group_dn(cn: str, ou: Optional[str] = None) -> str:
    """Build a group DN.

    Args:
        cn: The group's common name
        ou: OU to use. Defaults to settings.LDAP_OU_GROUPS

    Returns:
        Full DN string (e.g., 'cn=admins,ou=groups,dc=example,dc=com')
    """
    if ou is None:
        ou = settings.LDAP_OU_GROUPS
    return f"cn={cn},{build_ou(ou)}"


def build_computer_dn(hostname: str, ou: Optional[str] = None) -> str:
    """Build a computer DN.

    Args:
        hostname: The computer's hostname (CN)
        ou: OU to use. Defaults to settings.LDAP_OU_COMPUTERS

    Returns:
        Full DN string (e.g., 'cn=server1,ou=computers,dc=example,dc=com')
    """
    if ou is None:
        ou = settings.LDAP_OU_COMPUTERS
    return f"cn={hostname},{build_ou(ou)}"


def build_dns_dn(domain_name: str) -> str:
    """Build a DNS zone DN.

    Args:
        domain_name: The DNS domain name

    Returns:
        Full DN string (e.g., 'dc=example,dc=com,ou=dns,dc=example,dc=com')
    """
    # Convert domain to DC components
    dc_parts = ",".join(f"dc={part}" for part in domain_name.split("."))
    return f"{dc_parts},{build_ou(settings.LDAP_OU_DNS)}"


def build_asterisk_dn(context: str, ou: Optional[str] = None) -> str:
    """Build an Asterisk entry DN.

    Args:
        context: The Asterisk context
        ou: OU to use. Defaults to settings.LDAP_OU_AST

    Returns:
        Full DN string (e.g., 'cn=default,ou=asterisk,dc=example,dc=com')
    """
    if ou is None:
        ou = settings.LDAP_OU_AST
    return f"cn={context},{build_ou(ou)}"


def build_radius_dn(client_id: str, ou: Optional[str] = None) -> str:
    """Build a RADIUS client DN.

    Args:
        client_id: The RADIUS client identifier (IP or hostname)
        ou: OU to use. Defaults to settings.LDAP_OU_RADIUS

    Returns:
        Full DN string
    """
    if ou is None:
        ou = settings.LDAP_OU_RADIUS
    return f"cn={client_id},{build_ou(ou)}"


def build_krb_realm_dn(realm_name: str) -> str:
    """Build a Kerberos realm DN.

    Args:
        realm_name: The Kerberos realm name (e.g., 'EXAMPLE.COM')

    Returns:
        Full DN string (e.g., 'cn=EXAMPLE.COM,ou=kerberos,dc=example,dc=com')
    """
    # Convert realm to cn format
    return f"cn={realm_name},{build_ou(settings.LDAP_OU_KRB)}"


def build_krb_principal_dn(principal_name: str, realm_dn: Optional[str] = None) -> str:
    """Build a Kerberos principal DN.

    Args:
        principal_name: The principal name (e.g., 'jdoe@EXAMPLE.COM' or just 'jdoe')
        realm_dn: Realm container DN. Defaults to built from settings

    Returns:
        Full DN string
    """
    if realm_dn is None:
        realm_dn = build_krb_realm_dn(settings.LDAP_BASE_DN.split(",")[-1].replace("dc=", "").upper())

    # Extract just the principal name (before @)
    principal = principal_name.split("@")[0] if "@" in principal_name else principal_name
    return f"krbPrincipalName={principal},{realm_dn}"


def build_icap_dn(service_name: str, ou: Optional[str] = None) -> str:
    """Build an ICAP service DN.

    Args:
        service_name: The ICAP service name (CN)
        ou: OU to use. Defaults to settings.LDAP_OU_ICAP

    Returns:
        Full DN string
    """
    if ou is None:
        ou = getattr(settings, "LDAP_OU_ICAP", "ou=icap")
    return f"cn={service_name},{build_ou(ou)}"


def build_sendmail_dn(map_name: str, ou: Optional[str] = None) -> str:
    """Build a Sendmail map DN.

    Args:
        map_name: The map name
        ou: OU to use. Defaults to settings.LDAP_OU_SENDMAIL

    Returns:
        Full DN string
    """
    if ou is None:
        ou = settings.LDAP_OU_SENDMAIL
    return f"cn={map_name},{build_ou(ou)}"


def parse_dn(dn: str) -> dict:
    """Parse a distinguished name into components.

    Args:
        dn: The DN string to parse

    Returns:
        Dictionary of RDN components (e.g., {'uid': 'jdoe', 'ou': 'users'})
    """
    result = {}
    for rdn in dn.split(","):
        if "=" in rdn:
            key, value = rdn.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def get_parent_dn(dn: str) -> Optional[str]:
    """Get the parent DN of a given DN.

    Args:
        dn: The DN string

    Returns:
        Parent DN or None if already at base level
    """
    parts = dn.split(",", 1)
    return parts[1] if len(parts) > 1 else None


def get_ou_from_dn(dn: str) -> Optional[str]:
    """Extract the OU from a DN.

    Args:
        dn: The DN string

    Returns:
        OU value or None
    """
    parsed = parse_dn(dn)
    return parsed.get("ou")
