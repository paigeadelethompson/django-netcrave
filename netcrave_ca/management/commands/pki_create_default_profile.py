"""Management command to create a default certificate profile."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create a default certificate profile for common use cases."""

    help = "Create a default certificate profile"

    def add_arguments(self, parser):
        parser.add_argument(
            "--name",
            type=str,
            default="Default ACME Profile",
            help="Name for the new profile (default: Default ACME Profile)",
        )
        parser.add_argument(
            "--hostname-pattern",
            action="append",
            dest="hostname_patterns",
            default=[],
            help="Hostname pattern to match (can be specified multiple times)",
        )

    def handle(self, *args, **options):
        name = options["name"]
        hostname_patterns = options["hostname_patterns"]

        # Import here to avoid issues during early startup
        try:
            from netcrave_ca.models import CertificateTemplate, CertificateProfile

            # Try to find or create a default template
            try:
                template = CertificateTemplate.objects.get(is_default=True)
            except CertificateTemplate.DoesNotExist:
                self.stdout.write("No default template found. Creating one...")
                template = CertificateTemplate(
                    name="Default Template",
                    description="Default certificate template for ACME",
                    validity_days=365,
                    key_size=2048,
                    usage_key_encipherment=True,
                    usage_server_auth=True,
                    san_dns_pattern="*",
                )
                template.save()

            # Create the profile
            profile = CertificateProfile(
                name=name,
                description=f"Default profile for ACME certificate requests",
                template=template,
                hostname_patterns=hostname_patterns or ["*.example.com"],
                allow_kerberos_auth=True,
                enabled=True,
            )
            profile.save()

            self.stdout.write(self.style.SUCCESS(f"Created profile: {name}"))
            self.stdout.write(f"Template: {template.name}")
            self.stdout.write(f"Hostname patterns: {', '.join(profile.hostname_patterns)}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error creating profile: {e}"))
