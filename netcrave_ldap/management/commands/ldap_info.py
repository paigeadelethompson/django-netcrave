"""Management command to display LDAP tree information."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Display LDAP tree structure, entry counts, and schema info"

    def add_arguments(self, parser):
        parser.add_argument("--counts", action="store_true", help="Show entry counts per OU")
        parser.add_argument("--schema", action="store_true", help="Show schema information")

    def handle(self, *args, **options):
        self.stdout.write("LDAP Information")
