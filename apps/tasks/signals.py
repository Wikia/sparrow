import logging
import django.dispatch
from django.dispatch import receiver

logger = logging.getLogger(__name__)

ALL = ['task_status_changed', 'task_manager_request_status_update']

task_status_changed = django.dispatch.Signal(providing_args=['instance', ])
celery_request_status_update = django.dispatch.Signal(providing_args=['task_id', 'job_id', 'status'])


@receiver(celery_request_status_update)
def on_task_manager_request_status_update(sender, task_id, job_id, status, **kwargs):
    logger.debug('on_task_manager_request_status_update {} {}'.format(job_id, status))

    from tasks.models import Task, TaskStatus
    task = Task.objects.get(pk=task_id)
    if task is None:
        logger.warning('Could not find task #{}'.format(task_id))
        return

    sparrow_status = TaskStatus.from_celery_status(status)
    logger.debug('Task #{} received status update from celery ({}): status = {}'.format(
        task_id, job_id, TaskStatus.label(sparrow_status)))
    task.status = sparrow_status
    task.save()
