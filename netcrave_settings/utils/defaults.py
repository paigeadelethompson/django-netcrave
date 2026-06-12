"""
Default values for LDAP models.
"""

from datetime import date, timedelta

from django.conf import settings


def get_default_login_shell() -> str:
    """Get the default login shell."""
    return settings.LDAP_DEFAULT_LOGIN_SHELL


def get_default_gecos() -> str:
    """Get the default GECOS field."""
    return settings.LDAP_DEFAULT_GECOS


def get_default_uid_number() -> int:
    """Get the default starting UID number."""
    return settings.LDAP_DEFAULT_UID_NUMBER


def get_default_gid_number() -> int:
    """Get the default starting GID number."""
    return settings.LDAP_DEFAULT_GID_NUMBER


def get_default_dns_ttl() -> int:
    """Get the default DNS TTL in seconds."""
    return settings.LDAP_DEFAULT_DNS_TTL


def get_default_soa_serial() -> str:
    """Get the default SOA serial format string."""
    return settings.LDAP_DEFAULT_SOA_SERIAL


def get_default_soa_params() -> dict:
    """Get default SOA parameters.

    Returns:
        Dictionary with refresh, retry, expiry, minimum values
    """
    return {
        "refresh": settings.LDAP_DEFAULT_SOA_REFRESH,
        "retry": settings.LDAP_DEFAULT_SOA_RETRY,
        "expiry": settings.LDAP_DEFAULT_SOA_EXPIRY,
        "minimum": settings.LDAP_DEFAULT_SOA_MIN_TTL,
    }


def get_default_asterisk_context() -> str:
    """Get the default Asterisk context."""
    return settings.ASTERISK_DEFAULT_CONTEXT


def get_default_asterisk_priority() -> int:
    """Get the default Asterisk priority."""
    return settings.ASTERISK_DEFAULT_PRIORITY


def get_default_sip_transport() -> str:
    """Get the default SIP transport protocol."""
    return settings.ASTERISK_DEFAULT_TRANSPORT


def get_radius_defaults() -> dict:
    """Get RADIUS default values.

    Returns:
        Dictionary with auth_type, service_type, password_retry, etc.
    """
    return {
        "auth_type": settings.RADIUS_DEFAULT_AUTH_TYPE,
        "service_type": settings.RADIUS_DEFAULT_SERVICE_TYPE,
        "password_retry": settings.RADIUS_DEFAULT_PASSWORD_RETRY,
        "session_timeout": settings.RADIUS_DEFAULT_SESSION_TIMEOUT,
        "simultaneous_use": settings.RADIUS_DEFAULT_SIMULTANEOUS_USE,
        "framed_mtu": settings.RADIUS_DEFAULT_FRAMED_MTU,
    }


def get_krb_defaults() -> dict:
    """Get Kerberos default values.

    Returns:
        Dictionary with policy defaults
    """
    return {
        "max_pwd_life": settings.KRB_DEFAULT_MAX_PWD_LIFE,
        "min_pwd_life": settings.KRB_DEFAULT_MIN_PWD_LIFE,
        "pwd_min_length": settings.KRB_DEFAULT_PWD_MIN_LENGTH,
        "pwd_max_failure": settings.KRB_DEFAULT_PWD_MAX_FAILURE,
        "pwd_lockout_duration": settings.KRB_DEFAULT_PWD_LOCKOUT_DURATION,
        "ticket_lifetime": settings.KRB_DEFAULT_TICKET_LIFETIME,
        "renewable_age": settings.KRB_DEFAULT_RENEWABLE_AGE,
    }


def get_default_shadow_dates() -> dict:
    """Get default shadow password dates.

    Returns:
        Dictionary with shadowLastChange set to today
    """
    return {
        "shadow_last_change": (date.today().toordinal() - date(1970, 1, 1).toordinal()),
        "shadow_min": 0,
        "shadow_max": 99999,
        "shadow_warning": 7,
        "shadow_inactive": -1,
        "shadow_expire": -1,
        "shadow_flag": 0,
    }


def get_default_krb_principal_flags() -> dict:
    """Get default Kerberos principal flags.

    Returns:
        Dictionary with default flag values
    """
    return {
        "krb_up_enabled": True,
        "krb_last_successful_auth": None,
        "krb_last_failed_auth": None,
        "krb_login_failed_count": 0,
    }
