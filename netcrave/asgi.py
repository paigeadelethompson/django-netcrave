"""
ASGI config for netcrave project.

This module exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "netcrave_config.settings")

application = get_asgi_application()
