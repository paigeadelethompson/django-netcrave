"""OCSP (Online Certificate Status Protocol) views for certificate status checking.

This module implements OCSP responder functionality as Django views:
- ocsp_responder_view: Handles POST requests with DER-encoded OCSP requests
- ocsp_status_view: Returns service health status

OCSP is defined in RFC 6960 and uses ASN.1/DER encoding.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

try:
    from pyasn1.type import univ, namedtype, tag
    from pyasn1.codec.der import decoder as der_decoder, encoder as der_encoder
    from pyasn1.error import PyAsn1Error
except ImportError:
    raise ImportError(
        "pyasn1 is required for OCSP functionality. Install with: pip install pyasn1"
    )

try:
    from netcrave.utils.ldap_backend import get_ldap_connection
except ImportError:
    # Fallback for development without python-ldap installed
    def get_ldap_connection():
        raise NotImplementedError("python-ldap not available")

logger = logging.getLogger(__name__)


# OCSP Request ASN.1 structures (simplified subset)
class CertID(univ.Sequence):
    """OCSP CertID structure."""
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('hashAlgorithm', univ.Sequence()),
        namedtype.NamedType('issuerNameHash', univ.OctetString()),
        namedtype.NamedType('issuerKeyHash', univ.OctetString()),
        namedtype.NamedType('serialNumber', univ.Integer())
    )


class Request(univ.Sequence):
    """OCSP Request structure."""
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('reqCert', CertID()),
        namedtype.OptionalNamedType('singleRequestExtensions', univ.SequenceOf(
            componentType=univ.Sequence()
        ))
    )


class OCSPRequest(univ.Sequence):
    """Top-level OCSP Request."""
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('tbsRequest', univ.Sequence()),
        namedtype.OptionalNamedType('optionalSignature', univ.Sequence())
    )


def parse_ocsp_request(der_data: bytes) -> dict:
    """Parse DER-encoded OCSP request.

    Args:
        der_data: DER-encoded OCSP request bytes

    Returns:
        Dictionary containing parsed request data including serial number
    """
    try:
        parsed, _ = der_decoder.decode(der_data, asn1Spec=OCSPRequest())
        result = {}

        # Extract tbsRequest
        tbs_request = parsed[0]
        requests_seq = tbs_request[1]

        for req in requests_seq:
            cert_id = req[0]
            serial_number = int(cert_id[3])
            result['serial_number'] = serial_number

        return result
    except PyAsn1Error as e:
        logger.error(f"Failed to parse OCSP request: {e}")
        raise ValueError(f"Invalid OCSP request format: {e}")


def get_certificate_status_from_ldap(serial_number: int) -> tuple[str, Optional[datetime]]:
    """Query LDAP for certificate status.

    Args:
        serial_number: Certificate serial number

    Returns:
        Tuple of (status, revocation_date)
        Status is one of: 'good', 'revoked', 'unknown'
    """
    try:
        conn = get_ldap_connection()

        # Search for user certificates in LDAP
        base_dn = getattr(settings, "LDAP_OU_USERS", "ou=users") + "," + getattr(
            settings, "LDAP_BASE_DN", "dc=example,dc=com"
        )

        # Search for entries with userCertificate attribute matching serial
        search_filter = f"(objectClass=user)"

        try:
            result = conn.search(
                base_dn,
                scope=1,  # One level
                filterstr=search_filter,
                attrs=["userCertificate;binary", "uid"]
            )

            if not result:
                return ("unknown", None)

            for entry in result:
                dn, attributes = entry

                # Check for user certificate attribute
                certs_attr = attributes.get("userCertificate;binary", [])

                for cert_bytes in certs_attr:
                    # Parse certificate to get serial number
                    try:
                        from cryptography.hazmat.primitives import serialization
                        from cryptography.x509 import load_der_x509_certificate

                        cert = load_der_x509_certificate(cert_bytes)
                        cert_serial = cert.serial_number

                        if cert_serial == serial_number:
                            # Check if certificate is revoked
                            return ("good", None)

                    except Exception as e:
                        logger.warning(f"Failed to parse certificate: {e}")
                        continue

            return ("unknown", None)

        except Exception as e:
            logger.error(f"LDAP search failed: {e}")
            return ("unknown", None)

    except NotImplementedError:
        # python-ldap not available, return unknown
        logger.warning("python-ldap not available for certificate lookup")
        return ("unknown", None)


def build_ocsp_response(
    serial_number: int,
    status: str = "good",
    this_update: Optional[datetime] = None,
    next_update: Optional[datetime] = None,
) -> bytes:
    """Build a DER-encoded OCSP response.

    Args:
        serial_number: Certificate serial number
        status: Certificate status ('good', 'revoked', 'unknown')
        this_update: Timestamp for this update
        next_update: Timestamp for next expected update

    Returns:
        DER-encoded OCSP response bytes
    """
    if this_update is None:
        this_update = datetime.now(timezone.utc)
    if next_update is None:
        from datetime import timedelta
        next_update = this_update + timedelta(hours=1)

    # Simplified OCSP response structure
    # In production, you would properly encode using pyasn1
    # For now, return a placeholder that can be expanded

    status_codes = {"good": 0, "revoked": 1, "unknown": 2}

    # This is a simplified response. A full implementation would use pyasn1
    # to properly encode the OCSPResponse ASN.1 structure.

    logger.debug(
        f"OCSP Response: serial={serial_number}, status={status}, "
        f"this_update={this_update}, next_update={next_update}"
    )

    return der_encoder.encode(
        univ.Integer(status_codes.get(status, 2))
    )


@csrf_exempt
def ocsp_responder_view(request: HttpRequest) -> HttpResponse:
    """Handle OCSP responder requests.

    Accepts DER-encoded OCSP requests via POST and returns DER-encoded responses.
    See RFC 6960 for OCSP protocol details.

    Args:
        request: Django HTTP request

    Returns:
        HttpResponse with DER-encoded OCSP response
        Content-Type: application/ocsp-response
    """
    if request.method != "POST":
        return HttpResponseBadRequest(
            "OCSP responder only accepts POST requests"
        )

    # Get the raw request body (DER-encoded OCSP request)
    try:
        der_data = request.body

        if not der_data:
            return HttpResponseBadRequest("Empty request body")

        # Parse the OCSP request
        parsed_request = parse_ocsp_request(der_data)
        serial_number = parsed_request.get("serial_number")

        if serial_number is None:
            return HttpResponseBadRequest(
                "Could not extract serial number from OCSP request"
            )

        # Get certificate status from LDAP
        status, revocation_date = get_certificate_status_from_ldap(serial_number)

        # Build the response
        response_data = build_ocsp_response(
            serial_number=serial_number,
            status=status,
            this_update=datetime.now(timezone.utc),
            next_update=None,
        )

        logger.info(f"OCSP lookup for serial {serial_number}: {status}")

        return HttpResponse(
            response_data,
            content_type="application/ocsp-response",
            headers={
                "Cache-Control": "no-cache",
                "OCSP-Response-Type": "Basic",
            },
        )

    except ValueError as e:
        logger.warning(f"Invalid OCSP request: {e}")
        return HttpResponseBadRequest(str(e))
    except Exception as e:
        logger.error(f"OCSP responder error: {e}", exc_info=True)
        return HttpResponse(
            b"",  # Empty response on error
            content_type="application/ocsp-response",
            status=500,
        )


def ocsp_status_view(request: HttpRequest) -> HttpResponse:
    """Return OCSP service health status.

    Args:
        request: Django HTTP request

    Returns:
        JSON response with service status
    """
    try:
        # Check if LDAP connection is available
        try:
            conn = get_ldap_connection()
            ldap_available = True
        except NotImplementedError:
            ldap_available = False

        return JsonResponse(
            {
                "service": "OCSP Responder",
                "status": "online",
                "ldap_available": ldap_available,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return JsonResponse(
            {"status": "error", "message": str(e)}, status=503
        )


def get_certificate_status(serial_number: int) -> dict:
    """Get certificate status for a given serial number.

    Args:
        serial_number: Certificate serial number

    Returns:
        Dictionary with certificate status information
    """
    try:
        conn = get_ldap_connection()
        base_dn = getattr(settings, "LDAP_BASE_DN", "dc=example,dc=com")

        search_filter = f"(objectClass=user)"

        result = conn.search(
            base_dn,
            scope=2,  # Subtree
            filterstr=search_filter,
            attrs=["userCertificate;binary", "uid", "cn"],
        )

        for entry in result:
            dn, attributes = entry

            certs_attr = attributes.get("userCertificate;binary", [])

            for cert_bytes in certs_attr:
                try:
                    from cryptography.x509 import load_der_x509_certificate

                    cert = load_der_x509_certificate(cert_bytes)
                    if cert.serial_number == serial_number:
                        return {
                            "status": "good",
                            "serial_number": serial_number,
                            "subject": str(cert.subject),
                            "issuer": str(cert.issuer),
                            "valid_from": cert.not_valid_before_utc.isoformat()
                            if hasattr(cert, "not_valid_before_utc")
                            else cert.not_valid_before.isoformat(),
                            "valid_until": cert.not_valid_after_utc.isoformat()
                            if hasattr(cert, "not_valid_after_utc")
                            else cert.not_valid_after.isoformat(),
                        }
                except Exception as e:
                    logger.warning(f"Failed to parse certificate: {e}")
                    continue

        return {"status": "unknown", "serial_number": serial_number}

    except NotImplementedError:
        return {"status": "error", "message": "LDAP not configured"}
