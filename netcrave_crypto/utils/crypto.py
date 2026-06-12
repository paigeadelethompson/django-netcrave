"""
Password and cryptographic utilities for LDAP.
"""

import secrets
import string

from django.conf import settings

# Import cryptography with fallbacks
try:
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509 import (
        Name,
        NameOID,
        CertificateSigningRequestBuilder,
        X509CertificateBuilder,
        ExtensionOID,
        BasicConstraints,
        SubjectAlternativeName,
        load_pem_x50_certificate,
        load_pem_x509_csr,
        generate_serial_number,
    )
    from cryptography import x509
except ImportError:
    # Fallback when cryptography is not installed
    serialization = hashes = rsa = Name = NameOID = None  # type: ignore
    CertificateSigningRequestBuilder = X509CertificateBuilder = None  # type: ignore
    ExtensionOID = BasicConstraints = SubjectAlternativeName = None  # type: ignore
    load_pem_x50_certificate = load_pem_x509_csr = generate_serial_number = None  # type: ignore
    x509 = None  # type: ignore



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


def generate_rsa_keypair(
    key_size: int = 2048,
) -> tuple[str, str]:
    """Generate an RSA key pair.

    Args:
        key_size: Key size in bits (default 2048)

    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")

    return (private_pem, public_pem)


def generate_csr(
    common_name: str,
    private_key_pem: str,
    country: str = None,
    state_or_province: str = None,
    locality: str = None,
    organization: str = None,
    organizational_unit: str = None,
    email: str = None,
) -> str:
    """Generate a Certificate Signing Request (CSR).

    Args:
        common_name: CN for the certificate
        private_key_pem: Private key in PEM format
        country: Country Name (2 letter code)
        state_or_province: State or Province Name
        locality: Locality Name
        organization: Organization Name
        organizational_unit: Organizational Unit Name
        email: Email Address

    Returns:
        CSR in PEM format
    """
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509 import Name, NameOID

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("ascii"),
        password=None,
    )

    subject = Name([
        NameOID.COMMON_NAME(common_name),
    ])

    if country:
        subject = Name([NameOID.COUNTRY_NAME(country)] + list(subject))
    if state_or_province:
        subject = Name([NameOID.STATE_OR_PROVINCE_NAME(state_or_province)] + list(subject))
    if locality:
        subject = Name([NameOID.LOCALITY_NAME(locality)] + list(subject))
    if organization:
        subject = Name([NameOID.ORGANIZATION_NAME(organization)] + list(subject))
    if organizational_unit:
        subject = Name([NameOID.ORGANIZATIONAL_UNIT_NAME(organizational_unit)] + list(subject))
    if email:
        subject = Name([NameOID.EMAIL_ADDRESS(email)] + list(subject))

    csr = (
        CertificateSigningRequestBuilder()
        .subject_name(subject)
        .sign(private_key, hashes.SHA256())
    )

    return csr.public_bytes(serialization.Encoding.PEM).decode("ascii")


def sign_certificate(
    csr_pem: str,
    ca_private_key_pem: str,
    ca_cert_pem: str,
    validity_days: int = 365,
) -> str:
    """Sign a certificate using a CA.

    Args:
        csr_pem: CSR in PEM format
        ca_private_key_pem: CA private key in PEM format
        ca_cert_pem: CA certificate in PEM format
        validity_days: Certificate validity in days

    Returns:
        Signed certificate in PEM format
    """
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.x509 import load_pem_x509_certificate, load_pem_x509_csr
    from cryptography.x509.oid import ExtensionOID
    from datetime import datetime, timedelta

    csr = load_pem_x509_csr(csr_pem.encode("ascii"))
    ca_cert = load_pem_x509_certificate(ca_cert_pem.encode("ascii"))
    ca_private_key = serialization.load_pem_private_key(
        ca_private_key_pem.encode("ascii"),
        password=None,
    )

    subject = csr.subject
    issuer = ca_cert.subject

    cert_builder = (
        X509CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(csr.public_key())
        .serial_number(X509.generate_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
        .add_extension(
            csr.extensions.get_extension_for_class(
                cryptography.x509.BasicConstraints
            ).value,
            critical=False,
        )
    )

    # Add subject alternative name if present in CSR
    try:
        san = csr.extensions.get_extension_for_class(cryptography.x509.SubjectAlternativeName)
        cert_builder = cert_builder.add_extension(san.value, critical=False)
    except cryptography.x509.ExtensionNotFound:
        pass

    certificate = cert_builder.sign(
        ca_private_key,
        hashes.SHA256(),
    )

    return certificate.public_bytes(serialization.Encoding.PEM).decode("ascii")


def create_self_signed_ca(
    common_name: str,
    key_size: int = 2048,
    validity_days: int = 3650,  # 10 years
) -> tuple[str, str]:
    """Create a self-signed CA certificate.

    Args:
        common_name: CA name (CN)
        key_size: Key size in bits
        validity_days: Certificate validity in days

    Returns:
        Tuple of (private_key_pem, certificate_pem)
    """
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.x509 import Name, NameOID
    from datetime import datetime, timedelta

    private_key, _ = generate_rsa_keypair(key_size)

    subject = issuer = Name([NameOID.COMMON_NAME(common_name)])

    cert_builder = (
        X509CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(
            serialization.load_pem_private_key(
                private_key.encode("ascii"),
                password=None,
            ).public_key()
        )
        .serial_number(X509.generate_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
        .add_extension(
            cryptography.x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(
            serialization.load_pem_private_key(private_key.encode("ascii"), password=None),
            hashes.SHA256(),
        )
    )

    cert_pem = cert_builder.public_bytes(serialization.Encoding.PEM).decode("ascii")

    return (private_key, cert_pem)
