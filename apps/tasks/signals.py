import logging
import django.dispatch
from django.dispatch import receiver
import requests
from common.utils import build_absolute_uri

logger = logging.getLogger(__name__)

__all__ = ['task_status_changed', 'celery_request_status_update']

task_status_changed = django.dispatch.Signal(providing_args=['instance', ])
celery_request_status_update = django.dispatch.Signal(providing_args=['task_id', 'job_id', 'status'])


@receiver(celery_request_status_update)
def on_task_manager_request_status_update(sender, task_id, job_id, status, **kwargs):
    logger.debug('on_task_manager_request_status_update {} {}'.format(job_id, status))

    from tasks.models import TaskStatus
    sparrow_status = TaskStatus.from_celery_status(status)

    logger.debug('Task #{} received status update from celery ({}): status = {}'.format(
        task_id, job_id, TaskStatus.label(sparrow_status)))

    task_url = build_absolute_uri('/api/v1/tasks/{}/'.format(task_id))
    response = requests.patch(task_url, json={
        'status': sparrow_status
    })
    response.raise_for_status()
