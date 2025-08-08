"""App Tasks"""

# Standard Library
import logging

# Third Party
from celery import shared_task

logger = logging.getLogger(__name__)

# Create your tasks here


# anomalytracker Task
@shared_task
def anomalytracker_task():
    """anomalytracker Task"""

    pass
