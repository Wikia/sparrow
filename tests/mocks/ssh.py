# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class SSHConnectionMock(object):
    """ Simple mock class to simulate SSHConnection"""
    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass

    def execute(self, *args, **kwargs):
        return (0, None, None)
