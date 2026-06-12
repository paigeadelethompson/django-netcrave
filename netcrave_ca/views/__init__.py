"""Certificate Authority views for netcrave."""

from .ocsp import ocsp_responder_view, ocsp_status_view
from .acme import (
    acme_directory,
    acme_new_nonce,
    acme_new_account,
    acme_new_order,
    acme_revoke_cert,
    acme_order_status,
    acme_authorization,
    acme_challenge,
    acme_issue_cert,
    acme_list_certificates,
    acme_revoke_certificate,
    acme_get_certificate,
    acme_status,
)

__all__ = [
    # OCSP views
    "ocsp_responder_view",
    "ocsp_status_view",
    # ACME directory endpoints
    "acme_directory",
    "acme_new_nonce",
    "acme_new_account",
    "acme_new_order",
    "acme_revoke_cert",
    # ACME order/authorization endpoints
    "acme_order_status",
    "acme_authorization",
    "acme_challenge",
    # Simplified ACME endpoints for certificate management
    "acme_issue_cert",
    "acme_list_certificates",
    "acme_revoke_certificate",
    "acme_get_certificate",
    "acme_status",
]
