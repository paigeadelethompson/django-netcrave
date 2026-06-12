"""Management command to initialize the LDAP directory tree."""

from django.core.management.base import BaseCommand

from django.conf import settings
import ldap


class Command(BaseCommand):
    help = "Initialize the LDAP directory tree structure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without making them",
        )
        parser.add_argument(
            "--skip-defaults",
            action="store_true",
            help="Skip creating default counter values and policies",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        skip_defaults = options.get("skip_defaults", False)

        self.stdout.write("Initializing LDAP directory tree...")
        if dry_run:
            self.stdout.write(self.style.WARNING("(Dry run - no changes will be made)"))

        # Base OU entries to create
        ous = [
            settings.LDAP_OU_USERS,
            settings.LDAP_OU_GROUPS,
            settings.LDAP_OU_COMPUTERS,
            settings.LDAP_OU_DNS,
            settings.LDAP_OU_AST,
            settings.LDAP_OU_RADIUS,
            settings.LDAP_OU_KRB,
            settings.LDAP_OU_SENDMAIL,
        ]

        self.stdout.write("Creating organizational units...")

        if dry_run:
            for ou in ous:
                self.stdout.write(f"  Would create: {ou},{settings.LDAP_BASE_DN}")
        else:
            # Connect to LDAP
            conn = ldap.initialize(settings.LDAP_SERVER_URI)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)

            if settings.LDAP_BIND_DN and settings.LDAP_BIND_PASSWORD:
                conn.simple_bind_s(settings.LDAP_BIND_DN, settings.LDAP_BIND_PASSWORD)
            else:
                conn.simple_bind_s()

            for ou in ous:
                dn = f"ou={ou},{settings.LDAP_BASE_DN}"
                try:
                    conn.search_s(dn, ldap.SCOPE_BASE, "(objectClass=organizationalUnit)", ["ou"])
                    self.stdout.write(f"  exists: {dn}")
                except ldap.NO_SUCH_OBJECT:
                    conn.add_s(dn, [
                        ("objectClass", [b"top", b"organizationalUnit"]),
                        ("ou", ou.encode("utf-8")),
                    ])
                    self.stdout.write(self.style.SUCCESS(f"  created: {dn}"))

            conn.unbind()

        # Counter objects
        if not skip_defaults:
            self.stdout.write("\nCreating counter objects...")
            counters = [
                {"key": "uidNumber", "value": settings.LDAP_DEFAULT_UID_NUMBER},
                {"key": "gidNumber", "value": settings.LDAP_DEFAULT_GID_NUMBER},
            ]

            if dry_run:
                for counter in counters:
                    self.stdout.write(
                        f"  Would create: cn={counter['key']},cn=counters,{settings.LDAP_BASE_DN} = {counter['value']}"
                    )
            else:
                conn = ldap.initialize(settings.LDAP_SERVER_URI)
                conn.set_option(ldap.OPT_REFERRALS, 0)
                conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)

                if settings.LDAP_BIND_DN and settings.LDAP_BIND_PASSWORD:
                    conn.simple_bind_s(settings.LDAP_BIND_DN, settings.LDAP_BIND_PASSWORD)
                else:
                    conn.simple_bind_s()

                counter_dn = f"cn=counters,{settings.LDAP_BASE_DN}"
                try:
                    conn.search_s(counter_dn, ldap.SCOPE_BASE, "(objectClass=simpleSecurityObject)", [])
                except ldap.NO_SUCH_OBJECT:
                    conn.add_s(counter_dn, [
                        ("objectClass", [b"top", b"simpleSecurityObject"]),
                        ("cn", b"counters"),
                    ])

                for counter in counters:
                    cn_dn = f"cn={counter['key']},{counter_dn}"
                    try:
                        conn.search_s(cn_dn, ldap.SCOPE_BASE, "(objectClass=simpleSecurityObject)", [])
                        self.stdout.write(f"  exists: {cn_dn}")
                    except ldap.NO_SUCH_OBJECT:
                        conn.add_s(cn_dn, [
                            ("objectClass", [b"top", b"simpleSecurityObject"]),
                            ("cn", counter['key'].encode("utf-8")),
                            ("userPassword", str(counter['value']).encode("utf-8")),
                        ])
                        self.stdout.write(self.style.SUCCESS(f"  created: cn={counter['key']} = {counter['value']}"))

                conn.unbind()

        # Default Kerberos policies (if realm exists)
        if not skip_defaults:
            self.stdout.write("\nDefault Kerberos policy values:")
            self.stdout.write(f"  Max password life: {settings.KRB_DEFAULT_MAX_PWD_LIFE} seconds")
            self.stdout.write(f"  Min password life: {settings.KRB_DEFAULT_MIN_PWD_LIFE} seconds")
            self.stdout.write(f"  Password min length: {settings.KRB_DEFAULT_PWD_MIN_LENGTH}")
            self.stdout.write(f"  Max login failures: {settings.KRB_DEFAULT_PWD_MAX_FAILURE}")

        self.stdout.write(self.style.SUCCESS("\nLDAP tree initialization complete!"))
