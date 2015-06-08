# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
import mock


class ChromeMock(object):

    @staticmethod
    def create(*args, **kwargs):
        chrome_mock = mock.MagicMock()
        chrome_mock.execute_script.side_effect = ChromeMock.__navigation_timing_api_side_effect
        return chrome_mock

    @staticmethod
    def __navigation_timing_api_side_effect(*args, **kwargs):
        if args[0] == 'return new Date().getTime()':
            return 0
        if args[0] == 'return document.readyState':
            return 'complete'
        if args[0] == 'return window.performance.timing.loadEventEnd':
            return 7
        elif args[0] == 'return window.performance.timing':
            return dict(
                navigationStart=1,
                responseStart=2,
                responseEnd=3,
                domInteractive=4,
                domComplete=5,
                domContentLoadedEventEnd=6,
                loadEventEnd=7
            )
        else:
            raise Exception('Invalid __navigation_timing_api_side_effect invocation')