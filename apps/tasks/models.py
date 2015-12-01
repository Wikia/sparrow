# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django_enumfield import enum
import celery.states
from common.utils import build_absolute_uri

from testrunner.test_suites.simple import SimpleTestSuite

from .signals import task_status_changed



class TaskStatus(enum.Enum):
    PENDING = 0
    IN_PROGRESS = 1
    DONE = 2
    ERROR = -1

    labels = {
        PENDING: _('Pending'),
        IN_PROGRESS: _('In progress'),
        DONE: _('Done'),
        ERROR: _('Error'),
    }

    @classmethod
    def from_celery_status(cls, celery_status):
        if celery_status == celery.states.PENDING:
            return cls.PENDING
        if celery_status in (celery.states.RECEIVED, celery.states.STARTED):
            return cls.IN_PROGRESS
        if celery_status in celery.states.EXCEPTION_STATES:
            return cls.ERROR
        if celery_status == celery.states.SUCCESS:
            return cls.DONE

        raise ValueError('Unknown status: {0}'.format(celery_status))


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    test_run = models.ForeignKey('test_runs.TestRun', related_name='tasks')
    created = models.DateTimeField(auto_now_add=True)
    status = enum.EnumField(TaskStatus, default=TaskStatus.PENDING)
    job_id = models.UUIDField(blank=True, null=True)

    __original_status = None

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

        self.__original_status = self.status

    def save(self, *args, **kwargs):

        super(Task, self).save(*args, **kwargs)

        if self.__original_status != self.status:
            task_status_changed.send(self.__class__, instance=self)
            self.__original_status = self.status

    def run(self):
        results_uri=build_absolute_uri(reverse('testresult-list'))
        raw_result_uri=build_absolute_uri(reverse('testrawresult-list'))
        task_uri=build_absolute_uri(reverse('task-detail', args=[self.id, ]))
        test_run_uri=build_absolute_uri(reverse('testrun-detail', args=[self.test_run_id, ]))

        test_run = self.test_run
        suite = SimpleTestSuite()
        result = suite.run(
            task_id=self.id,
            retries=test_run.retries,
            url=test_run.test_run_uri,
            app_commit=test_run.app_commit,
            config_commit=test_run.config_commit,
            results_uri=results_uri,
            raw_result_uri=raw_result_uri,
            task_uri=task_uri,
            test_run_uri=test_run_uri
        )
        self.job_id = result.id
        self.status = TaskStatus.from_celery_status(result.status)
        self.save()

    def __repr__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __unicode__ = __repr__

    __str__ = __repr__
