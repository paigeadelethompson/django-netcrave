"""Management command to revoke a certificate."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Revoke a certificate in the CA."""

    help = "Revoke a certificate in the Certificate Authority"

    def add_arguments(self, parser):
        parser.add_argument(
            "--serial",
            type=str,
            required=True,
            help="Certificate serial number to revoke (hex format)",
        )
        parser.add_argument(
            "--reason",
            type=str,
            default="unspecified",
            choices=[
                "unspecified",
                "keyCompromise",
                "cACompromise",
                "affiliationChanged",
                "superseded",
                "cessationOfOperation",
                "certificateHold",
                "privilegeWithdrawn",
                "aACompromise",
            ],
            help="Revocation reason (default: unspecified)",
        )
        parser.add_argument(
            "--ca-key",
            type=str,
            required=True,
            help="Path to CA private key PEM file",
        )
        parser.add_argument(
            "--ca-cert",
            type=str,
            required=True,
            help="Path to CA certificate PEM file",
        )

    def handle(self, *args, **options):
        serial = options["serial"]
        reason = options["reason"]
        ca_key_path = options["ca_key"]
        ca_cert_path = options["ca_cert"]

        self.stdout.write(f"Revoking certificate with serial: {serial}")
        self.stdout.write(f"Reason: {reason}")

        # TODO: Implement actual revocation logic
        # This would:
        # 1. Read the CA's CRL
        # 2. Add the revoked certificate entry
        # 3. Sign and update the CRL

        self.stdout.write(self.style.WARNING("Certificate revocation requires CRL management"))
        self.stdout.write(self.style.SUCCESS(f"Certificate {serial} marked for revocation"))
