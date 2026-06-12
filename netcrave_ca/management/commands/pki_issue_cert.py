"""Management command to issue a certificate from the CA."""

import os

from django.core.management.base import BaseCommand

from netcrave_crypto.utils import generate_rsa_keypair, generate_csr, sign_certificate


class Command(BaseCommand):
    """Issue a new certificate signed by the CA."""

    help = "Issue a new certificate signed by the CA"

    def add_arguments(self, parser):
        parser.add_argument(
            "--common-name",
            type=str,
            required=True,
            help="Common Name for the certificate (required)",
        )
        parser.add_argument(
            "--ca-key",
            type=str,
            required=True,
            help="Path to CA private key PEM file",
        )
        parser.add_argument(
            "--ca-cert",
            type=str,
            required=True,
            help="Path to CA certificate PEM file",
        )
        parser.add_argument(
            "--country",
            type=str,
            default=None,
            help="Country Name (2 letter code)",
        )
        parser.add_argument(
            "--state",
            type=str,
            default=None,
            help="State or Province Name",
        )
        parser.add_argument(
            "--locality",
            type=str,
            default=None,
            help="Locality Name",
        )
        parser.add_argument(
            "--organization",
            type=str,
            default=None,
            help="Organization Name",
        )
        parser.add_argument(
            "--ou",
            type=str,
            default=None,
            dest="organizational_unit",
            help="Organizational Unit Name",
        )
        parser.add_argument(
            "--email",
            type=str,
            default=None,
            help="Email Address",
        )
        parser.add_argument(
            "--validity-days",
            type=int,
            default=365,
            help="Certificate validity in days (default: 365)",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=None,
            help="Directory to save certificate files (optional)",
        )

    def handle(self, *args, **options):
        common_name = options["common_name"]
        ca_key_path = options["ca_key"]
        ca_cert_path = options["ca_cert"]
        validity_days = options["validity_days"]
        output_dir = options["output_dir"]

        # Read CA key and certificate
        try:
            with open(ca_key_path, "r") as f:
                ca_private_key_pem = f.read()
            with open(ca_cert_path, "r") as f:
                ca_cert_pem = f.read()
        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(f"File not found: {e}"))
            return

        self.stdout.write(f"Issuing certificate for: {common_name}")
        self.stdout.write(f"CA Key: {ca_key_path}")
        self.stdout.write(f"CA Cert: {ca_cert_path}")
        self.stdout.write(f"Validity: {validity_days} days")

        # Generate client key pair
        self.stdout.write("Generating client key pair...")
        private_key, public_key = generate_rsa_keypair(key_size=2048)

        # Generate CSR
        self.stdout.write("Generating Certificate Signing Request...")
        country = options["country"]
        state = options["state"]
        locality = options["locality"]
        organization = options["organization"]
        ou = options["organizational_unit"]
        email = options["email"]

        csr_pem = generate_csr(
            common_name=common_name,
            private_key_pem=private_key,
            country=country,
            state_or_province=state,
            locality=locality,
            organization=organization,
            organizational_unit=ou,
            email=email,
        )

        # Sign the certificate
        self.stdout.write("Signing certificate with CA...")
        cert_pem = sign_certificate(
            csr_pem=csr_pem,
            ca_private_key_pem=ca_private_key_pem,
            ca_cert_pem=ca_cert_pem,
            validity_days=validity_days,
        )

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

            cert_name = common_name.replace(" ", "_").lower()

            key_path = os.path.join(output_dir, f"{cert_name}_private_key.pem")
            cert_path = os.path.join(output_dir, f"{cert_name}_certificate.pem")
            csr_path = os.path.join(output_dir, f"{cert_name}_request.csr")

            with open(key_path, "w") as f:
                f.write(private_key)
            with open(cert_path, "w") as f:
                f.write(cert_pem)
            with open(csr_path, "w") as f:
                f.write(csr_pem)

            self.stdout.write(self.style.SUCCESS(f"Private key saved to: {key_path}"))
            self.stdout.write(self.style.SUCCESS(f"Certificate saved to: {cert_path}"))
            self.stdout.write(self.style.SUCCESS(f"CSR saved to: {csr_path}"))
        else:
            # Output to stdout
            self.stdout.write("\n--- PRIVATE KEY ---")
            self.stdout.write(private_key)
            self.stdout.write("--- END PRIVATE KEY ---\n")

            self.stdout.write("\n--- CERTIFICATE ---")
            self.stdout.write(cert_pem)
            self.stdout.write("--- END CERTIFICATE ---\n")

        self.stdout.write(self.style.SUCCESS("Certificate issued successfully"))
