"""URL configuration for netcrave_ca app."""

from django.urls import path

from .views import (
    # OCSP views
    ocsp_responder_view,
    ocsp_status_view,
    # ACME directory endpoints
    acme_directory,
    acme_new_nonce,
    acme_new_account,
    acme_new_order,
    acme_revoke_cert,
    # ACME order/authorization endpoints
    acme_order_status,
    acme_authorization,
    acme_challenge,
    # Simplified ACME endpoints for certificate management
    acme_issue_cert,
    acme_list_certificates,
    acme_revoke_certificate,
    acme_get_certificate,
    acme_status,
)

app_name = "netcrave_ca"

urlpatterns = [
    # OCSP endpoints (RFC 6960)
    path("ocsp/", ocsp_responder_view, name="ocsp-responder"),
    path("ocsp/status/", ocsp_status_view, name="ocsp-status"),
    # ACME directory endpoint
    path("acme/directory", acme_directory, name="acme-directory"),
    # ACME nonce endpoint (RFC 8555 Section 7.2)
    path("acme/new-nonce", acme_new_nonce, name="acme-new-nonce"),
    # ACME account management (RFC 8555 Section 7.3)
    path("acme/new-account", acme_new_account, name="acme-new-account"),
    # ACME order management (RFC 8555 Section 7.4)
    path("acme/new-order", acme_new_order, name="acme-new-order"),
    path("acme/order/<str:order_id>/", acme_order_status, name="acme-order-status"),
    path(
        "acme/order/<str:order_id>/finalize",
        acme_order_status,
        name="acme-order-finalize",
    ),
    # ACME authorization endpoint (RFC 8555 Section 7.5)
    path("acme/authz/<str:authz_id>/", acme_authorization, name="acme-authz"),
    # ACME challenge endpoint (RFC 8555 Section 7.5)
    path(
        "acme/challenge/<str:challenge_id>/",
        acme_challenge,
        name="acme-challenge",
    ),
    # ACME revoke certificate (RFC 8555 Section 7.6)
    path("acme/revoke-cert", acme_revoke_cert, name="acme-revoke-cert"),
    # Certificate management endpoints
    path(
        "acme/certificates/<str:serial>/",
        acme_get_certificate,
        name="acme-get-certificate",
    ),
    path(
        "acme/certificates/",
        acme_list_certificates,
        name="acme-list-certificates",
    ),
    path(
        "acme/revoke-certificate/",
        acme_revoke_certificate,
        name="acme-revoke-certificate",
    ),
    # ACME issue certificate (simplified flow)
    path("acme/issue-cert", acme_issue_cert, name="acme-issue-cert"),
    # Service status
    path("acme/status", acme_status, name="acme-status"),
]
