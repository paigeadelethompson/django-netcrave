"""Netcrave ICAP application for Squid integration."""

from celery import Celery

default_app_config = "netcrave_icap.apps.NetcraveIcapConfig"

# Celery app configuration
celery_app = Celery("netcrave_icap")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks(["netcrave_icap"])
