"""Management command to backup LDAP database."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Backup LDAP database to LDIF or JSON format"

    def add_arguments(self, parser):
        parser.add_argument("output_file", help="Output file path for backup")
        parser.add_argument("--format", choices=["ldif", "json"], default="ldif", help="Backup format")

    def handle(self, *args, **options):
        output_file = options.get("output_file")
        fmt = options.get("format", "ldif")

        self.stdout.write(f"Backing up to: {output_file}")
        self.stdout.write(f"Format: {fmt}")
