# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django_enumfield import enum

from tasks.models import Task
from tasks.models import TaskStatus
from tasks.models import task_status_changed
from common.validators import GithubRevisionValidator

class TestRunStatus(enum.Enum):
    PENDING = 0
    IN_PROGRESS = 1
    DONE = 2
    ERROR = -1


class TestRun(models.Model):
    id = models.AutoField(primary_key=True)
    test_run_uri = models.URLField()
    main_revision = models.CharField(
        max_length=10,
        validators=[GithubRevisionValidator, ]
    )
    secondary_revision = models.CharField(
        max_length=10,
        validators=[GithubRevisionValidator, ]
    )
    status = enum.EnumField(TestRunStatus, default=TestRunStatus.PENDING)
    created = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return "{0}(#{1}): {2}@{3}".format(
            self.__class__.__name__,
            self.id,
            self.test_run_uri,
            self.main_revision
        )

    def __unicode__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __str__ = __unicode__


@receiver(task_status_changed, sender=Task)
def task_changed(sender, instance, **kwargs):
    """ Callback which synchronises TestRun status with Tasks statuses.

    Here lies simple logic which tries to synch TestRun status with all sub-Tasks
    statuses. It covers some very basic cases such as:
        * starting Task starts parent TestRun
        * any error in Task will result in setting error on parent TestRun
        * finishing all sub-Task will mark TestRun as done
    """
    test_run = instance.test_run

    if instance.status == TaskStatus.IN_PROGRESS and test_run.status == TestRunStatus.PENDING:
        test_run.status = TestRunStatus.IN_PROGRESS
        test_run.save()
    elif instance.status == TaskStatus.ERROR and test_run.status != TestRunStatus.ERROR:
        test_run.status = TestRunStatus.ERROR
        test_run.save()
    elif instance.status == TestRunStatus.DONE and test_run.status == TestRunStatus.IN_PROGRESS:
        test_run.status = TestRunStatus.DONE
        test_run.save()
