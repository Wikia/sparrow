# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class Action(object):
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = -1

    REQUIRED_PARAMS = ()

    def __init__(self, params=None, **kwargs):
        self.status = self.PENDING

        self.params = {}
        if params is not None:
            self.params.update(params)
        self.params.update(kwargs)

        self.result = {}
        self.raw_result = {}

        self.validate_params()

    def validate_params(self):
        for param_name in self.REQUIRED_PARAMS:
            if param_name not in self.params:
                raise KeyError(
                    "{class_name}: Parameter '{parameter}' is required.".format(class_name=self.__class__.__name__,
                                                                                parameter=param_name))

    @property
    def ok(self):
        return self.status == self.COMPLETED

    def run(self):
        raise NotImplementedError('Task.run() is an abstract method.')
