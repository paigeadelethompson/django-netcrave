"""
Django settings for ldap_management project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
import secrets
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    secrets.token_urlsafe(64),
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "netcrave_settings",
    "netcrave_ldap",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "netcrave_ldap.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "netcrave_ldap.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# LDAP Configuration
# LDAP Base DNs for each subtree
# Django will automatically construct full DNs based on these
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "dc=example,dc=com")

LDAP_OU_USERS = os.environ.get("LDAP_OU_USERS", "ou=users")
LDAP_OU_GROUPS = os.environ.get("LDAP_OU_GROUPS", "ou=groups")
LDAP_OU_COMPUTERS = os.environ.get("LDAP_OU_COMPUTERS", "ou=computers")
LDAP_OU_DNS = os.environ.get("LDAP_OU_DNS", "ou=dns")
LDAP_OU_AST = os.environ.get("LDAP_OU_AST", "ou=asterisk")
LDAP_OU_RADIUS = os.environ.get("LDAP_OU_RADIUS", "ou=radius")
LDAP_OU_KRB = os.environ.get("LDAP_OU_KRB", "ou=kerberos")
LDAP_OU_SENDMAIL = os.environ.get("LDAP_OU_SENDMAIL", "ou=sendmail")
LDAP_OU_POSTFIX = os.environ.get("LDAP_OU_POSTFIX", "ou=postfix")

# Auto-increment counter configuration
LDAP_COUNTER_BASE_DN = f"cn=counters,{LDAP_BASE_DN}"
LDAP_UID_COUNTER_ATTR = "uidNumberCounter"
LDAP_GID_COUNTER_ATTR = "gidNumberCounter"

# Default values for auto-increment counters (stored in LDAP)
LDAP_DEFAULT_UID_NUMBER = int(os.environ.get("LDAP_DEFAULT_UID_NUMBER", 1000))
LDAP_DEFAULT_GID_NUMBER = int(os.environ.get("LDAP_DEFAULT_GID_NUMBER", 100))

# POSIX defaults
LDAP_DEFAULT_LOGIN_SHELL = os.environ.get(
    "LDAP_DEFAULT_LOGIN_SHELL", "/bin/bash"
)
LDAP_DEFAULT_HOME_BASE = os.environ.get("LDAP_DEFAULT_HOME_BASE", "/home")
LDAP_DEFAULT_GECOS = os.environ.get("LDAP_DEFAULT_GECOS", "System User")

# DNS defaults
LDAP_DEFAULT_DNS_TTL = int(os.environ.get("LDAP_DEFAULT_DNS_TTL", 3600))
LDAP_DEFAULT_SOA_SERIAL = os.environ.get(
    "LDAP_DEFAULT_SOA_SERIAL", "%Y%m%d01"
)  # Date-based format: 2024010101
LDAP_DEFAULT_SOA_REFRESH = int(os.environ.get("LDAP_DEFAULT_SOA_REFRESH", 3600))
LDAP_DEFAULT_SOA_RETRY = int(os.environ.get("LDAP_DEFAULT_SOA_RETRY", 900))
LDAP_DEFAULT_SOA_EXPIRY = int(os.environ.get("LDAP_DEFAULT_SOA_EXPIRY", 604800))
LDAP_DEFAULT_SOA_MIN_TTL = int(os.environ.get("LDAP_DEFAULT_SOA_MIN_TTL", 86400))

# Asterisk defaults
ASTERISK_DEFAULT_CONTEXT = os.environ.get(
    "ASTERISK_DEFAULT_CONTEXT", "default"
)
ASTERISK_DEFAULT_PRIORITY = int(os.environ.get("ASTERISK_DEFAULT_PRIORITY", 1))
ASTERISK_DEFAULT_TRANSPORT = os.environ.get(
    "ASTERISK_DEFAULT_TRANSPORT", "udp"
)

# RADIUS defaults
RADIUS_DEFAULT_AUTH_TYPE = os.environ.get(
    "RADIUS_DEFAULT_AUTH_TYPE", "PAP"
)  # PAP, CHAP, MSCHAPV2
RADIUS_DEFAULT_SERVICE_TYPE = os.environ.get(
    "RADIUS_DEFAULT_SERVICE_TYPE", "Framed-User"
)
RADIUS_DEFAULT_PASSWORD_RETRY = int(os.environ.get("RADIUS_DEFAULT_PASSWORD_RETRY", 3))
RADIUS_DEFAULT_SESSION_TIMEOUT = int(os.environ.get("RADIUS_DEFAULT_SESSION_TIMEOUT", 3600))
RADIUS_DEFAULT_SIMULTANEOUS_USE = int(os.environ.get("RADIUS_DEFAULT_SIMULTANEOUS_USE", 1))
RADIUS_DEFAULT_FRAMED_MTU = int(os.environ.get("RADIUS_DEFAULT_FRAMED_MTU", 1500))

# Kerberos defaults
KRB_DEFAULT_MAX_PWD_LIFE = int(os.environ.get("KRB_DEFAULT_MAX_PWD_LIFE", 7776000))  # 90 days
KRB_DEFAULT_MIN_PWD_LIFE = int(os.environ.get("KRB_DEFAULT_MIN_PWD_LIFE", 86400))  # 1 day
KRB_DEFAULT_PWD_MIN_LENGTH = int(os.environ.get("KRB_DEFAULT_PWD_MIN_LENGTH", 8))
KRB_DEFAULT_PWD_MAX_FAILURE = int(os.environ.get("KRB_DEFAULT_PWD_MAX_FAILURE", 5))
KRB_DEFAULT_PWD_LOCKOUT_DURATION = int(os.environ.get("KRB_DEFAULT_PWD_LOCKOUT_DURATION", 900))  # 15 minutes
KRB_DEFAULT_TICKET_LIFETIME = int(os.environ.get("KRB_DEFAULT_TICKET_LIFETIME", 86400))  # 24 hours
KRB_DEFAULT_RENEWABLE_AGE = int(os.environ.get("KRB_DEFAULT_RENEWABLE_AGE", 604800))  # 7 days

# Password generation settings
PASSWORD_GENERATION_ENABLED = os.environ.get(
    "PASSWORD_GENERATION_ENABLED", "true"
).lower() == "true"
DEFAULT_PASSWORD_LENGTH = int(os.environ.get("DEFAULT_PASSWORD_LENGTH", 16))
DEFAULT_PASSWORD_INCLUDE_SYMBOLS = os.environ.get(
    "DEFAULT_PASSWORD_INCLUDE_SYMBOLS", "true"
).lower() == "true"

# UI/UX settings
ADMIN_LIST_PAGE_SIZE = int(os.environ.get("ADMIN_LIST_PAGE_SIZE", 25))
LDAP_SEARCH_SUGGESTION_LIMIT = int(os.environ.get("LDAP_SEARCH_SUGGESTION_LIMIT", 50))

# Schema validation settings
SCHEMA_VALIDATION_ENABLED = os.environ.get(
    "SCHEMA_VALIDATION_ENABLED", "true"
).lower() == "true"
