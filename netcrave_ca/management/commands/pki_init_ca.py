"""Management command to initialize a Certificate Authority."""

from django.core.management.base import BaseCommand

from netcrave_crypto.utils import create_self_signed_ca


class Command(BaseCommand):
    """Initialize a new self-signed CA certificate."""

    help = "Initialize a new self-signed Certificate Authority"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cn",
            type=str,
            default="Netcrave Root CA",
            help="Common Name for the CA (default: Netcrave Root CA)",
        )
        parser.add_argument(
            "--key-size",
            type=int,
            default=2048,
            choices=[1024, 2048, 4096],
            help="RSA key size in bits (default: 2048)",
        )
        parser.add_argument(
            "--validity-days",
            type=int,
            default=3650,
            help="Certificate validity in days (default: 3650 = 10 years)",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=None,
            help="Directory to save CA files (optional)",
        )

    def handle(self, *args, **options):
        cn = options["cn"]
        key_size = options["key_size"]
        validity_days = options["validity_days"]
        output_dir = options["output_dir"]

        self.stdout.write(f"Initializing CA: {cn}")
        self.stdout.write(f"Key size: {key_size} bits")
        self.stdout.write(f"Validity: {validity_days} days ({validity_days // 365} years)")

        private_key, certificate = create_self_signed_ca(
            common_name=cn,
            key_size=key_size,
            validity_days=validity_days,
        )

        if output_dir:
            import os
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ca_name = cn.replace(" ", "_").lower()

            os.makedirs(output_dir, exist_ok=True)

            key_path = os.path.join(output_dir, f"{ca_name}_private_key.pem")
            cert_path = os.path.join(output_dir, f"{ca_name}_certificate.pem")

            with open(key_path, "w") as f:
                f.write(private_key)
            with open(cert_path, "w") as f:
                f.write(certificate)

            self.stdout.write(self.style.SUCCESS(f"CA private key saved to: {key_path}"))
            self.stdout.write(self.style.SUCCESS(f"CA certificate saved to: {cert_path}"))
        else:
            # Output to stdout
            self.stdout.write("\n--- CA PRIVATE KEY (save this securely!) ---")
            self.stdout.write(private_key)
            self.stdout.write("--- END PRIVATE KEY ---\n")

            self.stdout.write("\n--- CA CERTIFICATE ---")
            self.stdout.write(certificate)
            self.stdout.write("--- END CERTIFICATE ---\n")

        self.stdout.write(self.style.SUCCESS("CA initialized successfully"))
