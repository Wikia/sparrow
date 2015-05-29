# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import django.dispatch
from django.utils.translation import ugettext as _
from django_enumfield import enum

from testrunner.test_suites.simple import SimpleTestSuite


task_status_changed = django.dispatch.Signal(providing_args=['instance', ])


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
        is_new = not self.pk

        super(Task, self).save(*args, **kwargs)

        if self.__original_status != self.status:
            task_status_changed.send(self.__class__, instance=self)
            self.__original_status = self.status

        # TODO: add more cases (resuming, aborting tasks)
        if (self.__original_status != self.status or is_new) and self.status == TaskStatus.PENDING:
            test_run = self.test_run
            suite = SimpleTestSuite()
            job_id = suite.run(
                task_id=self.id,
                retries=10,
                url=test_run.test_run_uri,
                app_commit=test_run.main_revision,
                config_commit=test_run.secondary_revision
            )
            self.job_id = job_id
            self.save()

    def __repr__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __unicode__ = __repr__

    __str__ = __repr__
