#!/usr/bin/env python3
"""Command-line interface for netcrave project."""

import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Determine settings path by looking for config files in order:
    # 1. /etc/django-netcrave (system-wide)
    # 2. ~/.django-netcrave (user-specific)

    etc_config = Path("/etc/django-netcrave")
    user_config = Path.home() / ".django-netcrave"

    settings_path = None

    if etc_config.exists():
        settings_path = etc_config
    elif user_config.exists():
        settings_path = user_config

    if settings_path:
        # Add the config directory to Python path so we can import settings
        sys.path.insert(0, str(settings_path))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    else:
        # No existing config found - use the project's default settings
        # Add netcrave_config to path so we can import settings from there
        project_base = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(project_base / "netcrave_config"))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
