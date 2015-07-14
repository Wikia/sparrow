# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class SSHConnectionMock(object):
    """ Simple mock class to simulate SSHConnection"""
    def __init__(self, *args, **kwargs):
        self.ret_stdout = ''
        self.ret_stderr = ''

    def close(self):
        pass

    def execute(self, *args, **kwargs):
        return (0, self.ret_stdout, self.ret_stdout)

def SSHConnectionMockBuilder(stdout='', stderr=''):
    def wrapper(*args,**kwargs):
        mock = SSHConnectionMock(*args, **kwargs)
        mock.ret_stdout = stdout
        mock.ret_stderr = stderr
        return mock
    return wrapper