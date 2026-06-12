"""ACME protocol utilities for netcrave CA."""

import hashlib
import base64
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from django.conf import settings


def b64url_encode(data: bytes) -> str:
    """Base64url encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def b64url_decode(data: str) -> bytes:
    """Base64url decode with proper padding."""
    # Add padding if needed
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


def generate_nonce() -> str:
    """Generate a nonce for ACME messages."""
    return b64url_encode(secrets.token_bytes(16))


def create_jwk_thumbprint(jwk: dict) -> str:
    """Create JWK thumbprint as specified in RFC 8555 Section 7.6."""
    # Sort keys alphabetically
    sorted_jwk = json.dumps(jwk, sort_keys=True, separators=(',', ':'))
    digest = hashlib.sha256(sorted_jwk.encode()).digest()
    return b64url_encode(digest)


def create_key_authorization(challenge_token: str, jwk_thumbprint: str) -> str:
    """Create key authorization for HTTP-01 challenge."""
    return f"{challenge_token}.{jwk_thumbprint}"


def get_acme_account_dn(uid: str) -> str:
    """Get the DN for an ACME account."""
    base_ou = getattr(settings, "LDAP_OU_ACME", "ou=acme")
    base_dn = getattr(settings, "LDAP_BASE_DN", "dc=example,dc=com")
    return f"uid={uid},{base_ou},{base_dn}"


def get_acme_certificate_dn(account_uid: str, domain: str) -> str:
    """Get the DN for an ACME-issued certificate."""
    base_ou = getattr(settings, "LDAP_OU_ACME", "ou=acme")
    base_dn = getattr(settings, "LDAP_BASE_DN", "dc=example,dc=com")
    # Use domain as part of DN (sanitized)
    sanitized_domain = domain.replace(".", ",dc=").rstrip(",dc=")
    return f"cn={domain},uid={account_uid},{base_ou},{base_dn}"


def check_kerberos_principal_access(principal: str, required_role: str = "network-admin") -> bool:
    """Check if a Kerberos principal has access to ACME operations.

    Args:
        principal: Kerberos principal name (e.g., user@REALM.COM)
        required_role: Required role for access

    Returns:
        True if principal has the required role, False otherwise
    """
    try:
        from netcrave.utils.ldap_backend import get_ldap_connection

        conn = get_ldap_connection()

        # Search for the principal in LDAP to check group membership
        base_dn = getattr(settings, "LDAP_OU_KRB", "ou=kerberos") + "," + \
                  getattr(settings, "LDAP_BASE_DN", "dc=example,dc=com")

        # Check if principal belongs to admins group or has admin role
        search_filter = f"(&(krbPrincipalName={principal})(|(memberOf=cn=admin,ou=groups,{base_dn}) (krbTicketFlags:1.2.840.113556.1.4.803:=1)))"

        try:
            result = conn.search(
                base_dn,
                scope=2,  # Subtree
                filterstr=search_filter,
                attrs=["krbPrincipalName"]
            )

            if result:
                return True

            # Fallback: check for group-based access
            groups_base = getattr(settings, "LDAP_OU_GROUPS", "ou=groups") + "," + \
                         getattr(settings, "LDAP_BASE_DN", "dc=example,dc=com")

            admin_groups = [
                "network-admins",
                "admins",
                "admin",
                "acme-admins"
            ]

            for group in admin_groups:
                group_dn = f"cn={group},{groups_base}"

                try:
                    # Check if principal is member of this group
                    result = conn.search(
                        group_dn,
                        scope=0,  # Base search
                        filterstr=f"(member={get_acme_account_dn(principal.split('@')[0])})",
                        attrs=["cn"]
                    )
                    if result:
                        return True
                except Exception:
                    continue

        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.warning(f"LDAP search failed for access check: {e}")

    except Exception as e:
        # Fallback - allow if principal is in admin realm or has @ADMIN suffix
        if '@ADMIN' in principal.upper() or principal.endswith('@REALM'):
            return True

    return False


def validate_acme_request_access(request, operation: str = "issue") -> tuple[bool, Optional[str]]:
    """Validate that the request has proper Kerberos access for ACME operations.

    Args:
        request: Django HTTP request
        operation: Operation being performed (issue, revoke, list)

    Returns:
        Tuple of (allowed, error_message)
    """
    # Check for Kerberos principal in request headers or environment

    principal = None

    # Try to get principal from various sources
    if hasattr(request, 'META'):
        principal = (
            request.META.get('HTTP_X_KERBEROS_PRINCIPAL') or
            request.META.get('X-Kerberos-Principal') or
            request.META.get('REMOTE_USER')
        )

    # If no principal found, allow admin access via staff/superuser
    if not principal:
        if hasattr(request, 'user'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(username='admin') if request.user.is_staff else None
                if user and user.is_superuser:
                    return True, None
            except Exception:
                pass

    # Check if principal has network-admin access
    if principal and check_kerberos_principal_access(principal, "network-admin"):
        return True, None

    return False, "Access denied: network-admin privileges required"


def format_acme_problem_details(error_type: str, detail: str = "") -> dict:
    """Format ACME problem document as per RFC 7807."""
    base_url = getattr(settings, "ACME_BASE_URL", "")

    problems = {
        "badNonce": {
            "type": f"{base_url} bad-nonce",
            "status": 400,
            "title": "Bad nonce"
        },
        "invalidContact": {
            "type": f"{base_url} invalid-contact",
            "status": 400,
            "title": "Invalid contact"
        },
        "accountDoesNotExist": {
            "type": f"{base_url} account-does-not-exist",
            "status": 400,
            "title": "Account does not exist"
        },
        "malformedRequest": {
            "type": f"{base_url} malformed-request",
            "status": 400,
            "title": "Malformed request"
        },
        "unauthorized": {
            "type": f"{base_url} unauthorized",
            "status": 403,
            "title": "Unauthorized"
        },
        "alreadyRevoked": {
            "type": f"{base_url} already-revoked",
            "status": 409,
            "title": "Certificate already revoked"
        },
    }

    problem = problems.get(error_type, problems["malformedRequest"])
    result = {
        "type": problem["type"],
        "status": problem["status"],
        "title": problem["title"],
    }

    if detail:
        result["detail"] = detail

    return result


def find_certificate_profile(hostname: str) -> Optional['CertificateProfile']:
    """Find the certificate profile that matches a hostname.

    Args:
        hostname: The hostname being requested

    Returns:
        CertificateProfile that matches, or None
    """
    try:
        from netcrave_ca.models import CertificateProfile
        from django.conf import settings as dj_settings

        # Only query if ACME is enabled
        acme_enabled = getattr(dj_settings, "ACME_ENABLED", True)
        if not acme_enabled:
            return None

        profiles = CertificateProfile.objects.filter(enabled=True)

        for profile in profiles:
            if profile.matches_hostname(hostname):
                # Check Kerberos requirements
                if profile.allow_kerberos_auth:
                    # Profile requires Kerberos - caller must verify this separately
                    pass
                return profile

    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.warning(f"Error finding certificate profile for {hostname}: {e}")

    return None


def get_default_certificate_profile() -> Optional['CertificateProfile']:
    """Get the default certificate profile for ACME requests.

    Returns:
        Default CertificateProfile, or None if not configured
    """
    try:
        from netcrave_ca.models import CertificateProfile

        # Try to find a profile marked as default
        try:
            return CertificateProfile.objects.get(is_default=True)
        except CertificateProfile.DoesNotExist:
            pass

        # Fallback: get first enabled profile
        profiles = CertificateProfile.objects.filter(enabled=True)
        if profiles.exists():
            return profiles.first()

    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.warning(f"Error getting default certificate profile: {e}")

    return None
