"""Management command to start the ICAP server worker.

This command starts a Celery worker that processes ICAP requests
from Squid proxy. The actual ICAP protocol handling is done by
Squid forwarding requests to Django via HTTP with custom headers.
"""

import os
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Start the Netcrave ICAP Celery worker."""

    help = "Start the Netcrave ICAP Celery worker for Squid integration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--queues",
            type=str,
            default="icap",
            help="Comma-separated list of queues to consume from (default: icap)",
        )
        parser.add_argument(
            "--concurrency",
            type=int,
            default=None,
            help="Number of concurrent workers (default: CELERY_WORKER_CONCURRENCY from settings)",
        )

    def handle(self, *args, **options):
        """Start the Celery worker."""
        import sys

        # Build celery command
        queues = options["queues"]
        concurrency = options["concurrency"]

        cmd_parts = ["celery -A netcrave_icap tasks worker"]

        if queues:
            cmd_parts.append(f"-Q {queues}")

        if concurrency:
            cmd_parts.append(f"-c {concurrency}")
        else:
            # Get from settings
            from django.conf import settings
            cmd_parts.append(f"-c {getattr(settings, 'CELERY_WORKER_CONCURRENCY', 4)}")

        cmd = " ".join(cmd_parts)

        self.stdout.write(self.style.SUCCESS(f"Starting ICAP worker with: {cmd}"))

        # Execute celery
        sys.exit(os.system(cmd))
