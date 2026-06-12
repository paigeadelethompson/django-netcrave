"""Celery tasks for ICAP processing."""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_icap_request(
    self,
    client_ip: str,
    method: str,
    request_headers: Dict[str, str],
    request_body: bytes,
    principal: Optional[str] = None,
) -> Dict[str, Any]:
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
    from netcrave_icap.models import ICAPLog

    try:
        # Log the incoming request
        log_entry = ICAPLog.objects.create(
            client_ip=client_ip,
            method=method,
            principal=principal or "anonymous",
            status="ALLOWED" if principal else "BLOCKED",
            response_code=200,
        )

        # Determine processing based on method
        if method == "OPTIONS":
            result = handle_options_request()
        elif method == "REQMOD":
            result = handle_reqmod_request(request_headers, request_body)
        elif method == "RESPMOD":
            result = handle_respmod_request(request_headers, request_body)
        else:
            result = {"error": f"Unsupported ICAP method: {method}"}

        # Update log with results
        log_entry.response_message = str(result.get("message", ""))
        if "processing_time_ms" in result:
            log_entry.processing_time_ms = result["processing_time_ms"]
        log_entry.save()

        return {
            "success": True,
            "log_id": log_entry.id,
            **result,
        }

    except Exception as exc:
        logger.error(f"ICAP request processing failed: {exc}")
        self.retry(exc=exc, countdown=2 ** self.request.retries)

        # Create error log entry
        try:
            ICAPLog.objects.create(
                client_ip=client_ip,
                method=method,
                principal=principal or "anonymous",
                status="ERROR",
                response_code=500,
                response_message=str(exc),
            )
        except Exception:
            pass

        return {
            "success": False,
            "error": str(exc),
        }


def handle_options_request() -> Dict[str, Any]:
    """Handle ICAP OPTIONS request."""
    return {
        "message": "ICAP service available",
        "methods": ["REQMOD", "RESPMOD", "OPTIONS"],
        "max_body_size": 0,
        "max_connections": 100,
        "preview_size": 1024,
        "transfer_complete": True,
    }


def handle_reqmod_request(
    headers: Dict[str, str],
    body: bytes,
) -> Dict[str, Any]:
    """Handle ICAP REQMOD request."""
    # Check if user is authenticated
    principal = headers.get("Principal", "")

    return {
        "message": "Request modification processed",
        "principal": principal or "anonymous",
        "action": "allow",
        "headers_modified": False,
        "body_modified": False,
    }


def handle_respmod_request(
    headers: Dict[str, str],
    body: bytes,
) -> Dict[str, Any]:
    """Handle ICAP RESPMOD request."""
    principal = headers.get("Principal", "")

    return {
        "message": "Response modification processed",
        "principal": principal or "anonymous",
        "action": "allow",
        "headers_modified": False,
        "body_modified": False,
    }


@shared_task
def log_icap_event(
    event_type: str,
    client_ip: str,
    details: Dict[str, Any],
) -> None:
    """
    Log an ICAP-related event.

    Args:
        event_type: Type of event (auth_success, auth_fail, etc.)
        client_ip: Client IP address
        details: Additional event details
    """
    logger.info(f"ICAP Event [{event_type}] from {client_ip}: {details}")
