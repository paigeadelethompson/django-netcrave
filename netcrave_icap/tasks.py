"""Celery tasks for ICAP processing."""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_icap_request(
    self,
    client_ip: str,
    method: str,
    request_headers: dict,
    request_body: bytes,
    principal: str = None,
) -> dict:
    """
    Process an ICAP request asynchronously.

    Args:
        client_ip: Client IP address
        method: ICAP method (REQMOD, RESPMOD, OPTIONS)
        request_headers: Dictionary of ICAP headers
        request_body: Raw request body bytes
        principal: Kerberos principal if authenticated

    Returns:
        Dictionary with processing results
    """
    from netcrave_icap.models import ICAPUserProfile
    from netcrave_ldap.utils.ldap_backend import get_ldap_connection

    try:
        # Validate access via LDAP for principal
        access_allowed = True
        if principal:
            try:
                conn = get_ldap_connection()
                search_base = getattr(
                    __import__("django.conf", fromlist=["settings"]).settings,
                    "LDAP_OU_ICAP_USERS",
                    "ou=icap-users," + __import__("django.conf", fromlist=["settings"]).settings.LDAP_BASE_DN
                )
                filter_str = f"(krbPrincipalName={principal})"
                result = conn.search(search_base, filterstr=filter_str)
                if result:
                    entry = result[0][1]
                    allow_attr = entry.get("icapAllowICAPAccess", [b"TRUE"])
                    access_allowed = allow_attr[0].decode().upper() == "TRUE"
            except Exception as e:
                logger.error(f"LDAP validation failed: {e}")
                access_allowed = False

        # Log the incoming request (to syslog via logger)
        if access_allowed:
            logger.info(
                "ICAP request allowed",
                extra={
                    "client_ip": client_ip,
                    "method": method,
                    "principal": principal or "anonymous",
                },
            )
            status = "ALLOWED"
        else:
            logger.warning(
                "ICAP request blocked",
                extra={
                    "client_ip": client_ip,
                    "method": method,
                    "principal": principal or "anonymous",
                },
            )
            status = "BLOCKED"

        # Determine processing based on method
        if method == "OPTIONS":
            result = handle_options_request()
        elif method in ("REQMOD", "RESPMOD"):
            result = handle_mod_request(method, request_headers, request_body)
        else:
            result = {"error": f"Unsupported ICAP method: {method}"}

        return {
            "success": access_allowed,
            "status": status,
            **result,
        }

    except Exception as exc:
        logger.error(f"ICAP request processing failed: {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)

        return {
            "success": False,
            "error": str(exc),
        }


def handle_options_request() -> dict:
    """Handle ICAP OPTIONS request."""
    return {
        "message": "ICAP service available",
        "methods": ["REQMOD", "RESPMOD", "OPTIONS"],
        "max_body_size": 0,
        "max_connections": 100,
        "preview_size": 1024,
        "transfer_complete": True,
    }


def handle_mod_request(
    method: str,
    headers: dict,
    body: bytes,
) -> dict:
    """Handle REQMOD or RESPMOD requests."""
    principal = headers.get("Principal", "")

    return {
        "message": f"{method} request processed",
        "principal": principal or "anonymous",
        "action": "allow",
        "headers_modified": False,
        "body_modified": False,
    }


@shared_task
def log_icap_event(
    event_type: str,
    client_ip: str,
    details: dict,
) -> None:
    """
    Log an ICAP-related event to syslog.

    Args:
        event_type: Type of event (auth_success, auth_fail, etc.)
        client_ip: Client IP address
        details: Additional event details
    """
    logger.info(f"ICAP Event [{event_type}] from {client_ip}: {details}")
