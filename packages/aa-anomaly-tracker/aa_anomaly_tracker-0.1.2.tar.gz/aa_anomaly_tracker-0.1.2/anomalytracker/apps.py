"""App Configuration"""

# Django
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from anomalytracker import __version__
from django.core.management import call_command


def clean_permissions(sender, **kwargs):
    call_command("clean_permissions", "anomalytracker")


class AnomalytrackerConfig(AppConfig):
    name = "anomalytracker"

    def ready(self):
        post_migrate.connect(clean_permissions, sender=self)



class anomalytrackerConfig(AppConfig):
    """App Config"""

    name = "anomalytracker"
    label = "anomalytracker"
    verbose_name = f"anomalytracker App v{__version__}"

    def ready(self):
        post_migrate.connect(clean_permissions, sender=self)
