# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from celery import states

from testrunner import app as celery_app
from tasks.signals import celery_request_status_update


class BaseTask(celery_app.Task):
    FIRST = 0
    MIDDLE = 1
    LAST = 2

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position

    def on_start(self, task_uri):
        celery_request_status_update.send(self.__class__, task_uri=task_uri, job_id=self.request.id,
                                          status=states.STARTED)

    def on_success(self, retval, task_id, args, kwargs):
        if self.position == self.LAST:
            celery_request_status_update.send(self.__class__, task_uri=kwargs['task_uri'], job_id=self.request.id,
                                              status=states.SUCCESS)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        celery_request_status_update.send(self.__class__, task_uri=kwargs['task_uri'], job_id=self.request.id,
                                          status=states.FAILURE)

