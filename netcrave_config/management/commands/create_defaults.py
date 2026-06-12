"""Management command to create default users, groups, and domains."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default LDAP entries (users, groups, domains, policies)"

    def add_arguments(self, parser):
        parser.add_argument("--skip-users", action="store_true", help="Skip creating default users")
        parser.add_argument("--skip-groups", action="store_true", help="Skip creating default groups")
        parser.add_argument("--skip-domains", action="store_true", help="Skip creating DNS domains")
        parser.add_argument("--skip-policies", action="store_true", help="Skip creating Kerberos policies")

    def handle(self, *args, **options):
        self.stdout.write("Creating default LDAP entries...")
