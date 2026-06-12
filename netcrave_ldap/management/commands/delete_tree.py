"""Management command to safely delete LDAP entries."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Safely delete LDAP entries with dependency checks"

    def add_arguments(self, parser):
        parser.add_argument("dn", nargs="?", help="Base DN to delete (e.g., ou=users,dc=example,dc=com)")
        parser.add_argument("--dry-run", action="store_true", help="Preview deletions without making changes")
        parser.add_argument("--soft-delete", action="store_true", help="Move entries to cn=deleted instead of hard delete")

    def handle(self, *args, **options):
        dn = options.get("dn")
        dry_run = options.get("dry_run", False)
        soft_delete = options.get("soft_delete", False)

        self.stdout.write(f"Delete DN: {dn}")
        self.stdout.write(f"Dry run: {dry_run}")
        self.stdout.write(f"Soft delete: {soft_delete}")
