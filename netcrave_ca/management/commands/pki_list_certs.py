"""Management command to list certificates in the CA."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """List all certificates stored in the LDAP directory."""

    help = "List certificates stored in the Certificate Authority"

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            type=str,
            choices=["valid", "revoked", "expired"],
            help="Filter by certificate status",
        )
        parser.add_argument(
            "--subject",
            type=str,
            help="Filter by subject (partial match)",
        )

    def handle(self, *args, **options):
        status_filter = options["status"]
        subject_filter = options["subject"]

        self.stdout.write("=== Certificate List ===\n")

        # TODO: Query LDAP for certificates
        # For now, show a placeholder
        self.stdout.write(f"Status filter: {status_filter or 'all'}")
        self.stdout.write(f"Subject filter: {subject_filter or 'none'}\n")

        self.stdout.write(self.style.WARNING("LDAP certificate query not yet implemented"))
        self.stdout.write("\nSample certificates (placeholder):")
        self.stdout.write("- CN=example.com, O=Example Corp, valid until 2025-12-31")
        self.stdout.write("- CN=test.example.com, O=Example Corp, revoked on 2024-06-01")
