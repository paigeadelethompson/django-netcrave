"""
Password and cryptographic utilities for LDAP.
"""

import secrets
import string

from django.conf import settings


def generate_password(length: int = None, include_symbols: bool = None) -> str:
    """Generate a secure random password.

    Args:
        length: Password length. Defaults to DEFAULT_PASSWORD_LENGTH
        include_symbols: Include special characters. Defaults to DEFAULT_PASSWORD_INCLUDE_SYMBOLS

    Returns:
        Randomly generated password string
    """
    if length is None:
        length = settings.DEFAULT_PASSWORD_LENGTH
    if include_symbols is None:
        include_symbols = settings.DEFAULT_PASSWORD_INCLUDE_SYMBOLS

    # Character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Build character pool
    pool = lowercase + uppercase + digits
    if include_symbols:
        pool += symbols

    # Ensure at least one of each required type
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
    ]

    if include_symbols:
        password.append(secrets.choice(symbols))

    # Fill remaining characters
    for _ in range(length - len(password)):
        password.append(secrets.choice(pool))

    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)

    return "".join(password)


def hash_password_ssha(password: str) -> str:
    """Hash a password using SSHA (Salted SHA).

    Args:
        password: Plain text password

    Returns:
        {SSHA}encoded{hash}{salt} string
    """
    import base64
    import hashlib
    import os

    # Generate random salt
    salt = os.urandom(8)

    # Hash password with salt
    sha_hash = hashlib.sha1(password.encode("utf-8") + salt).digest()

    # Combine hash and salt, then base64 encode
    hashed = base64.b64encode(sha_hash + salt).decode("ascii")

    return "{SSHA}" + hashed


def verify_password_ssha(password: str, stored_hash: str) -> bool:
    """Verify a password against an SSHA hash.

    Args:
        password: Plain text password to verify
        stored_hash: Stored {SSHA}hash string

    Returns:
        True if password matches, False otherwise
    """
    import base64
    import hashlib

    # Remove {SSHA} prefix
    if stored_hash.startswith("{SSHA}"):
        encoded = stored_hash[6:]
    else:
        encoded = stored_hash

    # Decode from base64
    decoded = base64.b64decode(encoded)

    # Last 8 bytes are the salt
    salt = decoded[-8:]
    hash_value = decoded[:-8]

    # Hash provided password with extracted salt
    computed = hashlib.sha1(password.encode("utf-8") + salt).digest()

    return computed == hash_value


def generate_kerberos_salt(principal_name: str, realm: str) -> str:
    """Generate a Kerberos salt for a principal.

    Args:
        principal_name: Principal name (without realm)
        realm: Kerberos realm

    Returns:
        Salt string in format used by Kerberos
    """
    # Default salt is typically the principal name
    return f"{principal_name}@{realm}"
