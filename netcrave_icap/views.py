"""ICAP views for the netcrave_icap app."""

from typing import Dict, Any, Optional

from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
)
from django.views.decorators.csrf import csrf_exempt

import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def icap_responder_view(request: HttpRequest) -> HttpResponse:
    """
    Handle ICAP requests from Squid proxy.

    This view handles ICAP REQMOD, RESPMOD, and OPTIONS requests.
    It validates Kerberos principals for access control via LDAP.

    Args:
        request: Django HTTP request

    Returns:
        HttpResponse with ICAP response
    """
    # Determine ICAP method from X-ICAP header or method
    icap_method = request.META.get("X_ICAP_METHOD", request.method)

    # Extract Kerberos principal
    principal = _extract_principal(request)

    # Validate access via LDAP
    if not _validate_access(principal):
        return _build_icap_response(403, "Forbidden", {"error": "Access denied"})

    # Process based on method
    if icap_method == "OPTIONS":
        result = _handle_options_request()
    elif icap_method in ("REQMOD", "RESPMOD"):
        result = _handle_mod_request(icap_method, request)
    else:
        result = {"error": f"Unsupported ICAP method: {icap_method}"}

    return _build_icap_response(200, "OK", result)


@csrf_exempt
def icap_status_view(request: HttpRequest) -> HttpResponse:
    """
    Handle ICAP service status requests.

    Args:
        request: Django HTTP request

    Returns:
        JSON response with service status
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    return JsonResponse(
        {
            "status": "running",
            "service": "netcrave-icap",
            "version": "1.0",
            "methods_supported": ["REQMOD", "RESPMOD", "OPTIONS"],
            "kerberos_auth": True,
        }
    )


def _extract_principal(request: HttpRequest) -> Optional[str]:
    """
    Extract Kerberos principal from the request.

    Args:
        request: Django HTTP request

    Returns:
        Principal string or None
    """
    # Check Authorization header for Kerberos ticket
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if auth_header.startswith("Kerberos "):
        return auth_header[9:]  # Remove "Kerberos " prefix

    # Check custom principal header
    return request.META.get("HTTP_PRINCIPAL")


def _validate_access(principal: Optional[str]) -> bool:
    """
    Validate that the principal has ICAP access via LDAP.

    Args:
        principal: Kerberos principal or None for anonymous

    Returns:
        True if access is allowed, False otherwise
    """
    from netcrave_icap.models import ICAPService

    # Get the default ICAP service configuration from LDAP
    try:
        service = ICAPService.objects.get(cn="default")
        if service.icap_allow_anonymous and not principal:
            return True
    except ICAPService.DoesNotExist:
        # No service configured, use settings fallback
        from django.conf import settings
        if not principal and getattr(settings, "ICAP_ALLOW_ANONYMOUS", False):
            return True

    # If no principal, access denied (and anonymous not allowed)
    if not principal:
        return False

    # Check LDAP for user's ICAP access control entry
    try:
        from netcrave_ldap.utils.ldap_backend import get_ldap_connection

        conn = get_ldap_connection()

        # Search for user by principal in icapUser entries
        search_base = getattr(
            settings, "LDAP_OU_ICAP_USERS", "ou=icap-users," + settings.LDAP_BASE_DN
        )
        filter_str = f"(icapKerberosServicePrincipal={principal})"

        result = conn.search(search_base, filterstr=filter_str)

        if result:
            # Check if access is allowed
            entry = result[0][1]
            allow_attr = entry.get("icapAllowICAPAccess", [b"TRUE"])
            return allow_attr[0].decode().upper() == "TRUE"

    except Exception as e:
        logger.error(f"LDAP validation failed: {e}")

    # Default deny
    return False


def _handle_options_request() -> Dict[str, Any]:
    """Handle ICAP OPTIONS request."""
    from django.conf import settings

    port = getattr(settings, "ICAP_SERVER_PORT", 1344)

    return {
        "message": "ICAP service available",
        "methods": ["REQMOD", "RESPMOD", "OPTIONS"],
        "max_body_size": 0,
        "max_connections": 100,
        "preview_size": 1024,
        "transfer_complete": True,
        "service_port": port,
    }


def _handle_mod_request(
    method: str, request: HttpRequest
) -> Dict[str, Any]:
    """Handle REQMOD or RESPMOD requests."""
    return {
        "message": f"{method} request processed",
        "action": "allow",
        "headers_modified": False,
        "body_modified": False,
    }


def _build_icap_response(
    status_code: int, message: str, data: Dict[str, Any]
) -> HttpResponse:
    """
    Build an ICAP response.

    Args:
        status_code: HTTP/ICAP status code
        message: Status message
        data: Additional data to include

    Returns:
        HttpResponse with ICAP response
    """
    response = HttpResponse()
    response["ICAP-Version"] = "1.0"
    response["Service"] = "Netcrave-ICAP/1.0"
    response["ISTag"] = "20240101"

    if status_code == 200:
        response.status_code = 200
        response["Allow"] = "204"

    return response
