"""Management command to generate LDAP configuration file."""

import getpass
from django.core.management.base import BaseCommand

from pathlib import Path


class Command(BaseCommand):
    help = "Generate django-ldap configuration file interactively"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default=None,
            help="Output path for config file (default: ~/.django-ldap/config.py)",
        )
        parser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Overwrite existing configuration file",
        )

    def handle(self, *args, **options):
        output_path = options.get("output")
        force = options.get("force", False)

        if output_path:
            config_file = Path(output_path)
        else:
            config_file = Path.home() / ".django-ldap" / "config.py"

        # Ensure parent directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists and not forcing
        if config_file.exists() and not force:
            overwrite = input(
                f"Configuration already exists at {config_file}. Overwrite? (y/N): "
            ).strip().lower()
            if overwrite not in ("y", "yes"):
                self.stdout.write("Configuration generation cancelled.")
                return

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("LDAP Server Configuration"))
        self.stdout.write(self.style.SUCCESS("=" * 60 + "\n"))

        config = {}

        # LDAP Server URI
        server_uri = input(
            "LDAP Server URI (e.g., ldap://localhost or ldaps://ldap.example.com): "
        ).strip()
        if not server_uri:
            server_uri = "ldap://localhost"
        config["LDAP_SERVER_URI"] = server_uri

        # Bind DN
        self.stdout.write(self.style.SUCCESS("\nBind credentials (for Django to connect to LDAP)"))
        bind_dn = input(
            "Bind DN (e.g., cn=admin,dc=example,dc=com) [empty for anonymous]: "
        ).strip()

        if bind_dn:
            config["LDAP_BIND_DN"] = bind_dn
            config["LDAP_BIND_PASSWORD"] = getpass.getpass("Bind Password: ")
        else:
            config["LDAP_BIND_DN"] = ""
            config["LDAP_BIND_PASSWORD"] = ""

        # Base DN
        self.stdout.write(self.style.SUCCESS("\nBase Distinguished Name (root of your LDAP directory)"))
        base_dn = input(
            "Base DN (e.g., dc=example,dc=com): "
        ).strip()
        if not base_dn:
            base_dn = "dc=example,dc=com"
        config["LDAP_BASE_DN"] = base_dn

        # Extract domain for Kerberos realm
        domain_parts = []
        for part in base_dn.split(","):
            if part.startswith("dc="):
                domain_parts.append(part[3:])
        default_realm = ".".join(domain_parts).upper() if domain_parts else "EXAMPLE.COM"

        # Organizational Units
        self.stdout.write(self.style.SUCCESS("\nOrganizational Unit Structure"))

        ou_users = input("Users OU (default: ou=users): ").strip()
        config["LDAP_OU_USERS"] = ou_users if ou_users else "ou=users"

        ou_groups = input("Groups OU (default: ou=groups): ").strip()
        config["LDAP_OU_GROUPS"] = ou_groups if ou_groups else "ou=groups"

        ou_computers = input("Computers OU (default: ou=computers): ").strip()
        config["LDAP_OU_COMPUTERS"] = ou_computers if ou_computers else "ou=computers"

        ou_dns = input("DNS OU (default: ou=dns): ").strip()
        config["LDAP_OU_DNS"] = ou_dns if ou_dns else "ou=dns"

        ou_ast = input("Asterisk OU (default: ou=asterisk): ").strip()
        config["LDAP_OU_AST"] = ou_ast if ou_ast else "ou=asterisk"

        ou_radius = input("RADIUS OU (default: ou=radius): ").strip()
        config["LDAP_OU_RADIUS"] = ou_radius if ou_radius else "ou=radius"

        ou_krb = input("Kerberos OU (default: ou=kerberos): ").strip()
        config["LDAP_OU_KRB"] = ou_krb if ou_krb else "ou=kerberos"

        ou_sendmail = input("Sendmail OU (default: ou=sendmail): ").strip()
        config["LDAP_OU_SENDMAIL"] = ou_sendmail if ou_sendmail else "ou=sendmail"

        ou_postfix = input("Postfix OU (default: ou=postfix): ").strip()
        config["LDAP_OU_POSTFIX"] = ou_postfix if ou_postfix else "ou=postfix"

        # Auto-increment counters
        self.stdout.write(self.style.SUCCESS("\nAuto-Increment Counter Settings"))

        uid_start = input("Starting UID number (default: 1000): ").strip()
        config["LDAP_DEFAULT_UID_NUMBER"] = int(uid_start) if uid_start else 1000

        gid_start = input("Starting GID number (default: 100): ").strip()
        config["LDAP_DEFAULT_GID_NUMBER"] = int(gid_start) if gid_start else 100

        # POSIX defaults
        self.stdout.write(self.style.SUCCESS("\nPOSIX Account Defaults"))

        login_shell = input("Default login shell (default: /bin/bash): ").strip()
        config["LDAP_DEFAULT_LOGIN_SHELL"] = login_shell if login_shell else "/bin/bash"

        home_base = input("Home directory base path (default: /home): ").strip()
        config["LDAP_DEFAULT_HOME_BASE"] = home_base if home_base else "/home"

        # DNS defaults
        self.stdout.write(self.style.SUCCESS("\nDNS Defaults"))

        dns_ttl = input("Default DNS TTL in seconds (default: 3600): ").strip()
        config["LDAP_DEFAULT_DNS_TTL"] = int(dns_ttl) if dns_ttl else 3600

        # Asterisk defaults
        self.stdout.write(self.style.SUCCESS("\nAsterisk Defaults"))

        ast_context = input("Default Asterisk context (default: default): ").strip()
        config["ASTERISK_DEFAULT_CONTEXT"] = ast_context if ast_context else "default"

        ast_transport = input("Default SIP transport (udp/tcp/tls, default: udp): ").strip()
        config["ASTERISK_DEFAULT_TRANSPORT"] = ast_transport if ast_transport else "udp"

        # RADIUS defaults
        self.stdout.write(self.style.SUCCESS("\nRADIUS Defaults"))

        radius_auth = input("Default RADIUS auth type (PAP/CHAP/MSCHAPV2, default: PAP): ").strip()
        config["RADIUS_DEFAULT_AUTH_TYPE"] = radius_auth if radius_auth else "PAP"

        radius_service = input("Default service type (default: Framed-User): ").strip()
        config["RADIUS_DEFAULT_SERVICE_TYPE"] = radius_service if radius_service else "Framed-User"

        # Kerberos defaults
        self.stdout.write(self.style.SUCCESS("\nKerberos Defaults"))

        print(f"Detected realm from Base DN: {default_realm}")
        use_default = input(f"Use this realm? (Y/n): ").strip().lower()
        if use_default in ("", "y", "yes"):
            config["KRB_REALM"] = default_realm
        else:
            config["KRB_REALM"] = input("Enter Kerberos realm: ").strip().upper()

        max_pwd_life = input("Default password max life in seconds (default: 7776000 / 90 days): ").strip()
        config["KRB_DEFAULT_MAX_PWD_LIFE"] = int(max_pwd_life) if max_pwd_life else 7776000

        min_pwd_life = input("Default password min life in seconds (default: 86400 / 1 day): ").strip()
        config["KRB_DEFAULT_MIN_PWD_LIFE"] = int(min_pwd_life) if min_pwd_life else 86400

        pwd_min_length = input("Minimum password length (default: 8): ").strip()
        config["KRB_DEFAULT_PWD_MIN_LENGTH"] = int(pwd_min_length) if pwd_min_length else 8

        pwd_max_failure = input("Maximum login failures before lockout (default: 5): ").strip()
        config["KRB_DEFAULT_PWD_MAX_FAILURE"] = int(pwd_max_failure) if pwd_max_failure else 5

        ticket_lifetime = input("Default ticket lifetime in seconds (default: 86400 / 24 hours): ").strip()
        config["KRB_DEFAULT_TICKET_LIFETIME"] = int(ticket_lifetime) if ticket_lifetime else 86400

        # Generate and write the configuration file
        config_content = self.generate_config_file(config)
        config_file.write_text(config_content)

        self.stdout.write(self.style.SUCCESS(f"\n{config_file} has been created successfully!"))
        self.stdout.write(self.style.SUCCESS("\nNext steps:"))
        self.stdout.write("  1. Copy the config file to your project root or set DJANGO_SETTINGS_MODULE")
        self.stdout.write("  2. Run 'netcrave migrate' to set up the database")
        self.stdout.write("  3. Run 'netcrave init_tree' to create LDAP directory structure")

    def generate_config_file(self, config: dict) -> str:
        """Generate config.py file content from configuration dictionary."""
        base_dn = config["LDAP_BASE_DN"]
        ldap_counter_base_dn = f"cn=counters,{base_dn}"

        lines = [
            '"""Django LDAP Configuration."""',
            "",
            "import os",
            "from pathlib import Path",
            "",
            "# Build paths inside the project like this: BASE_DIR / 'subdir'.",
            'BASE_DIR = Path(__file__).resolve().parent.parent',
            "",
            "# SECURITY WARNING: keep the secret key used in production secret!",
            "import secrets",
            f'SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "{secrets.token_urlsafe(64)}")',
            "",
            "# SECURITY WARNING: don't run with debug turned on in production!",
            'DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"',
            "",
            'ALLOWED_HOSTS = ["*"]',
            "",
            "# Application definition",
            "INSTALLED_APPS = [",
            '    "django.contrib.admin",',
            '    "django.contrib.auth",',
            '    "django.contrib.contenttypes",',
            '    "django.contrib.sessions","',
            '    "django.contrib.messages",',
            '    "django.contrib.staticfiles",',
            '    "netcrave_ldap",',
            '    "netcrave_ca",',
            '    "netcrave_config",',
            "]",
            "",
            "MIDDLEWARE = [",
            '    "django.middleware.security.SecurityMiddleware",',
            '    "django.contrib.sessions.middleware.SessionMiddleware",',
            '    "django.middleware.common.CommonMiddleware",',
            '    "django.middleware.csrf.CsrfViewMiddleware",',
            '    "django.contrib.auth.middleware.AuthenticationMiddleware",',
            '    "django.contrib.messages.middleware.MessageMiddleware",',
            '    "django.middleware.clickjacking.XFrameOptionsMiddleware",',
            "]",
            "",
            'ROOT_URLCONF = "netcrave.urls"',
            "",
            "TEMPLATES = [",
            "    {",
            '        "BACKEND": "django.template.backends.django.DjangoTemplates",',
            f'        "DIRS": [BASE_DIR / "templates"],',
            '        "APP_DIRS": True,',
            '        "OPTIONS": {',
            '            "context_processors": [',
            '                "django.template.context_processors.debug",',
            '                "django.template.context_processors.request",',
            '                "django.contrib.auth.context_processors.auth",',
            '                "django.contrib.messages.context_processors.messages",',
            "            ],",
            "        },",
            "    },",
            "]",
            "",
            'WSGI_APPLICATION = "netcrave.wsgi.application"',
            "",
            "# Database",
            'DATABASES = {',
            '    "default": {',
            '        "ENGINE": "django.db.backends.sqlite3",',
            '        "NAME": BASE_DIR / "db.sqlite3",',
            "    }",
            "}",
            "",
            "# Password validation",
            "AUTH_PASSWORD_VALIDATORS = [",
            '    {',
            '        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",',
            "    },",
            '    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},',
            '    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},',
            '    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},',
            "]",
            "",
            "# Internationalization",
            'LANGUAGE_CODE = "en-us"',
            'TIME_ZONE = "UTC"',
            "USE_I18N = True",
            "USE_TZ = True",
            "",
            "# Static files (CSS, JavaScript, Images)",
            'STATIC_URL = "static/"',
            'STATICFILES_DIRS = [BASE_DIR / "static"]',
            'STATIC_ROOT = BASE_DIR / "staticfiles"',
            "",
            "# Default primary key field type",
            'DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"',
            "",
            "# ==============================================================================",
            "# LDAP Configuration",
            "# ==============================================================================",
            "",
            "# LDAP Server Settings",
            f'LDAP_SERVER_URI = os.environ.get("LDAP_SERVER_URI", "{config["LDAP_SERVER_URI"]}")',
            f'LDAP_BIND_DN = os.environ.get("LDAP_BIND_DN", "{config["LDAP_BIND_DN"]}")',
            f'LDAP_BIND_PASSWORD = os.environ.get("LDAP_BIND_PASSWORD", "{config["LDAP_BIND_PASSWORD"]}")',
            "",
            "# Base DNs for each subtree",
            f'LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "{base_dn}")',
            "",
            f'LDAP_OU_USERS = os.environ.get("LDAP_OU_USERS", "{config["LDAP_OU_USERS"]}")',
            f'LDAP_OU_GROUPS = os.environ.get("LDAP_OU_GROUPS", "{config["LDAP_OU_GROUPS"]}")',
            f'LDAP_OU_COMPUTERS = os.environ.get("LDAP_OU_COMPUTERS", "{config["LDAP_OU_COMPUTERS"]}")',
            f'LDAP_OU_DNS = os.environ.get("LDAP_OU_DNS", "{config["LDAP_OU_DNS"]}")',
            f'LDAP_OU_AST = os.environ.get("LDAP_OU_AST", "{config["LDAP_OU_AST"]}")',
            f'LDAP_OU_RADIUS = os.environ.get("LDAP_OU_RADIUS", "{config["LDAP_OU_RADIUS"]}")',
            f'LDAP_OU_KRB = os.environ.get("LDAP_OU_KRB", "{config["LDAP_OU_KRB"]}")',
            f'LDAP_OU_SENDMAIL = os.environ.get("LDAP_OU_SENDMAIL", "{config["LDAP_OU_SENDMAIL"]}")',
            f'LDAP_OU_POSTFIX = os.environ.get("LDAP_OU_POSTFIX", "{config["LDAP_OU_POSTFIX"]}")',
            "",
            "# Auto-increment counter configuration",
            f"LDAP_COUNTER_BASE_DN = os.environ.get('LDAP_COUNTER_BASE_DN', '{ldap_counter_base_dn}')",
            "",
            "# Default values for auto-increment counters",
            f'LDAP_DEFAULT_UID_NUMBER = int(os.environ.get("LDAP_DEFAULT_UID_NUMBER", {config["LDAP_DEFAULT_UID_NUMBER"]}))',
            f'LDAP_DEFAULT_GID_NUMBER = int(os.environ.get("LDAP_DEFAULT_GID_NUMBER", {config["LDAP_DEFAULT_GID_NUMBER"]}))',
            "",
            "# POSIX defaults",
            f'LDAP_DEFAULT_LOGIN_SHELL = os.environ.get("LDAP_DEFAULT_LOGIN_SHELL", "{config["LDAP_DEFAULT_LOGIN_SHELL"]}")',
            f'LDAP_DEFAULT_HOME_BASE = os.environ.get("LDAP_DEFAULT_HOME_BASE", "{config["LDAP_DEFAULT_HOME_BASE"]}")',
            "",
            "# DNS defaults",
            f'LDAP_DEFAULT_DNS_TTL = int(os.environ.get("LDAP_DEFAULT_DNS_TTL", {config["LDAP_DEFAULT_DNS_TTL"]}))',
            "",
            "# Asterisk defaults",
            f'ASTERISK_DEFAULT_CONTEXT = os.environ.get("ASTERISK_DEFAULT_CONTEXT", "{config["ASTERISK_DEFAULT_CONTEXT"]}")',
            f'ASTERISK_DEFAULT_TRANSPORT = os.environ.get("ASTERISK_DEFAULT_TRANSPORT", "{config["ASTERISK_DEFAULT_TRANSPORT"]}")',
            "",
            "# RADIUS defaults",
            f'RADIUS_DEFAULT_AUTH_TYPE = os.environ.get("RADIUS_DEFAULT_AUTH_TYPE", "{config["RADIUS_DEFAULT_AUTH_TYPE"]}")',
            f'RADIUS_DEFAULT_SERVICE_TYPE = os.environ.get("RADIUS_DEFAULT_SERVICE_TYPE", "{config["RADIUS_DEFAULT_SERVICE_TYPE"]}")',
            "",
            "# Kerberos defaults",
            f'KRB_DEFAULT_MAX_PWD_LIFE = int(os.environ.get("KRB_DEFAULT_MAX_PWD_LIFE", {config["KRB_DEFAULT_MAX_PWD_LIFE"]}))',
            f'KRB_DEFAULT_MIN_PWD_LIFE = int(os.environ.get("KRB_DEFAULT_MIN_PWD_LIFE", {config["KRB_DEFAULT_MIN_PWD_LIFE"]}))',
            f'KRB_DEFAULT_PWD_MIN_LENGTH = int(os.environ.get("KRB_DEFAULT_PWD_MIN_LENGTH", {config["KRB_DEFAULT_PWD_MIN_LENGTH"]}))',
            f'KRB_DEFAULT_PWD_MAX_FAILURE = int(os.environ.get("KRB_DEFAULT_PWD_MAX_FAILURE", {config["KRB_DEFAULT_PWD_MAX_FAILURE"]}))',
            f'KRB_DEFAULT_TICKET_LIFETIME = int(os.environ.get("KRB_DEFAULT_TICKET_LIFETIME", {config["KRB_DEFAULT_TICKET_LIFETIME"]}))',
            "",
            "# End of configuration",
        ]

        return "\n".join(lines)
