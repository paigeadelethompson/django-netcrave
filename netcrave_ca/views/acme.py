"""ACME views for netcrave CA."""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

try:
    from ..utils.acme import (
        b64url_encode,
        b64url_decode,
        generate_nonce,
        create_jwk_thumbprint,
        validate_acme_request_access,
        format_acme_problem_details,
        get_acme_account_dn,
    )
except ImportError as e:
    raise ImportError(f"netcrave_ca utils not available: {e}")


logger = logging.getLogger(__name__)


# ACME directory endpoints
def acme_directory(request: HttpRequest) -> HttpResponse:
    """Return the ACME directory with all supported endpoints.

    RFC 8555 Section 7.1.1
    """
    base_url = getattr(settings, "ACME_BASE_URL", "")

    directory = {
        "keyChange": f"{base_url}acme/key-change",
        "newAccount": f"{base_url}acme/new-account",
        "newNonce": f"{base_url}acme/new-nonce",
        "newOrder": f"{base_url}acme/new-order",
        "revokeCert": f"{base_url}acme/revoke-cert",
    }

    return JsonResponse(directory, json_dumps_params={"indent": 2})


def acme_new_nonce(request: HttpRequest) -> HttpResponse:
    """Return a fresh nonce for ACME requests.

    RFC 8555 Section 7.2
    """
    nonce = generate_nonce()

    response = HttpResponse(status=204)
    response["Replay-Nonce"] = nonce
    response["Cache-Control"] = "no-store"
    return response


@csrf_exempt
def acme_new_account(request: HttpRequest) -> HttpResponse:
    """Create a new ACME account.

    RFC 8555 Section 7.3
    """
    # Validate access - only network admins can create accounts
    allowed, error_msg = validate_acme_request_access(request, "create-account")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        problem = format_acme_problem_details("malformedRequest")
        return JsonResponse(problem, status=400)

    # Extract account details from request
    contact = body.get("contact", [])
    agreement = body.get("agreement", "")

    # Validate required fields
    if not agreement:
        problem = format_acme_problem_details(
            "badRequest",
            "Agreement to CA terms is required"
        )
        return JsonResponse(problem, status=400)

    # Generate account JWK thumbprint (simplified - in production would use actual key)
    jwk = body.get("key", {})
    if not jwk:
        problem = format_acme_problem_details(
            "malformedRequest",
            "Public key required for account creation"
        )
        return JsonResponse(problem, status=400)

    try:
        thumbprint = create_jwk_thumbprint(jwk)
    except Exception as e:
        logger.error(f"Failed to create JWK thumbprint: {e}")
        problem = format_acme_problem_details("malformedRequest")
        return JsonResponse(problem, status=400)

    # Create account record (would be saved to database/LDAP)
    account_id = thumbprint[:16]  # Simplified account ID

    response_data = {
        "key": jwk,
        "contact": contact,
        "agreement": agreement,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "status": "valid",
    }

    response = JsonResponse(response_data, status=201)
    response["Location"] = f"{get_acme_account_dn(account_id)}"
    return response


@csrf_exempt
def acme_new_order(request: HttpRequest) -> HttpResponse:
    """Create a new certificate order.

    RFC 8555 Section 7.4
    """
    # Validate access
    allowed, error_msg = validate_acme_request_access(request, "order")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        problem = format_acme_problem_details("malformedRequest")
        return JsonResponse(problem, status=400)

    # Extract identifiers from order
    identifiers = body.get("identifiers", [])
    if not identifiers:
        problem = format_acme_problem_details(
            "badRequest",
            "At least one identifier is required"
        )
        return JsonResponse(problem, status=400)

    # Process each identifier (currently only supports DNS type)
    order_status = {
        "status": "pending",
        "expires": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "identifiers": identifiers,
        "authorizations": [],
        "finalize": f"{getattr(settings, 'ACME_BASE_URL', '')}acme/order/{generate_nonce()[:16]}/finalize",
    }

    return JsonResponse(order_status, status=201)


@csrf_exempt
def acme_revoke_cert(request: HttpRequest) -> HttpResponse:
    """Revoke a certificate.

    RFC 8555 Section 7.6
    """
    # Validate access - only network admins can revoke certificates
    allowed, error_msg = validate_acme_request_access(request, "revoke")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        problem = format_acme_problem_details("malformedRequest")
        return JsonResponse(problem, status=400)

    # Extract certificate to revoke
    cert_b64 = body.get("certificate")
    if not cert_b64:
        problem = format_acme_problem_details(
            "badRequest",
            "Certificate required for revocation"
        )
        return JsonResponse(problem, status=400)

    try:
        cert_data = b64url_decode(cert_b64)
    except Exception as e:
        logger.error(f"Failed to decode certificate: {e}")
        problem = format_acme_problem_details("malformedRequest")
        return JsonResponse(problem, status=400)

    # Check if certificate is already revoked (would query LDAP)
    # For now, assume successful revocation

    response_data = {
        "status": "revoked",
        "revokedAt": datetime.now(timezone.utc).isoformat(),
    }

    return JsonResponse(response_data)


def acme_order_status(request: HttpRequest, order_id: str) -> HttpResponse:
    """Get status of an order.

    RFC 8555 Section 7.4
    """
    # Validate access
    allowed, error_msg = validate_acme_request_access(request, "order-status")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    order_status = {
        "status": "pending",
        "expires": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "identifiers": [],
        "authorizations": [],
        "finalize": f"{getattr(settings, 'ACME_BASE_URL', '')}acme/order/{order_id}/finalize",
    }

    return JsonResponse(order_status)


def acme_authorization(request: HttpRequest, authz_id: str) -> HttpResponse:
    """Get status of an authorization.

    RFC 8555 Section 7.5
    """
    # Validate access
    allowed, error_msg = validate_acme_request_access(request, "authz")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    authz_status = {
        "status": "valid",
        "expires": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "identifier": {"type": "dns", "value": "example.com"},
        "challenges": [],
    }

    return JsonResponse(authz_status)


def acme_challenge(request: HttpRequest, challenge_id: str) -> HttpResponse:
    """Process an ACME challenge.

    RFC 8555 Section 7.5
    """
    # Validate access
    allowed, error_msg = validate_acme_request_access(request, "challenge")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        body = {}

    challenge_status = {
        "type": body.get("type", "http-01"),
        "status": "valid",
        "validated": datetime.now(timezone.utc).isoformat(),
    }

    return JsonResponse(challenge_status)


# Simplified ACME views for certificate management
def acme_issue_cert(request: HttpRequest) -> HttpResponse:
    """Issue a new certificate via ACME flow.

    POST /acme/issue-cert

    Request body:
    {
        "csr": "<base64url-encoded CSR>",
        "domain": "example.com",
        "validity_days": 90
    }
    """
    allowed, error_msg = validate_acme_request_access(request, "issue")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        problem = format_acme_problem_details("malformedRequest")
        return JsonResponse(problem, status=400)

    csr_b64 = body.get("csr")
    domain = body.get("domain", "")

    if not csr_b64 or not domain:
        problem = format_acme_problem_details(
            "badRequest",
            "CSR and domain are required"
        )
        return JsonResponse(problem, status=400)

    # Verify access to specific domain (network admins can issue for any)
    # In production, would check if principal has permission for this domain

    response_data = {
        "status": "pending",
        "message": "Certificate issuance request received",
        "domain": domain,
        "order_url": f"{getattr(settings, 'ACME_BASE_URL', '')}acme/order/{generate_nonce()[:16]}",
    }

    return JsonResponse(response_data, status=202)


def acme_list_certificates(request: HttpRequest) -> HttpResponse:
    """List certificates issued via ACME.

    GET /acme/certificates

    Query params:
    - owner: Filter by owner principal
    - status: Filter by status (valid, revoked, expired)
    """
    allowed, error_msg = validate_acme_request_access(request, "list")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    owner_filter = request.GET.get("owner")
    status_filter = request.GET.get("status")

    certificates = []

    # In production, would query LDAP for certificate entries
    # This is a placeholder response

    response_data = {
        "certificates": certificates,
        "count": len(certificates),
    }

    return JsonResponse(response_data)


def acme_revoke_certificate(request: HttpRequest) -> HttpResponse:
    """Revoke an issued certificate.

    POST /acme/revoke-certificate

    Request body:
    {
        "serial": "certificate-serial-number",
        "reason": 0  // 0 = unspecified, see RFC 5280
    }
    """
    allowed, error_msg = validate_acme_request_access(request, "revoke")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        problem = format_acme_problem_details("malformedRequest")
        return JsonResponse(problem, status=400)

    serial = body.get("serial")
    reason = body.get("reason", 0)

    if not serial:
        problem = format_acme_problem_details(
            "badRequest",
            "Certificate serial is required"
        )
        return JsonResponse(problem, status=400)

    # Validate revocation reason
    valid_reasons = [0, 1, 2, 3, 4, 5, 6, 9, 10, 11]
    if reason not in valid_reasons:
        problem = format_acme_problem_details(
            "badRequest",
            f"Invalid revocation reason. Must be one of: {valid_reasons}"
        )
        return JsonResponse(problem, status=400)

    response_data = {
        "status": "revoked",
        "serial": serial,
        "reason": reason,
        "revokedAt": datetime.now(timezone.utc).isoformat(),
    }

    return JsonResponse(response_data)


def acme_get_certificate(request: HttpRequest, serial: str) -> HttpResponse:
    """Retrieve an issued certificate by serial.

    GET /acme/certificates/<serial>
    """
    allowed, error_msg = validate_acme_request_access(request, "read")
    if not allowed:
        problem = format_acme_problem_details("unauthorized", error_msg)
        return JsonResponse(problem, status=403)

    # In production, would query LDAP for the certificate
    response_data = {
        "serial": serial,
        "status": "pending",
        "message": "Certificate retrieval would be implemented here",
    }

    return JsonResponse(response_data)


# Helper for OCSP - also check Kerberos access
def ocsp_with_kerberos_auth(request: HttpRequest, operation: str) -> tuple[bool, Optional[str]]:
    """Check Kerberos access for OCSP operations.

    Args:
        request: Django HTTP request
        operation: Operation type (check-status, health)

    Returns:
        Tuple of (allowed, error_message)
    """
    allowed, error_msg = validate_acme_request_access(request, operation)

    # For status checks, allow more lenient access
    if operation == "health":
        return True, None

    return allowed, error_msg


def acme_status(request: HttpRequest) -> HttpResponse:
    """Return ACME service status.

    GET /acme/status
    """
    try:
        from netcrave.utils.ldap_backend import get_ldap_connection

        conn = get_ldap_connection()
        ldap_available = True
    except (ImportError, NotImplementedError):
        ldap_available = False

    return JsonResponse({
        "service": "ACME",
        "status": "online",
        "version": "draft-12",
        "directory": f"{getattr(settings, 'ACME_BASE_URL', '')}acme/directory",
        "ldap_available": ldap_available,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
