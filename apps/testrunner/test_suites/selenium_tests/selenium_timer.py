# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class SeleniumTimer(object):
    def __init__(self, driver):
        self.__driver = driver
        self.__measurements = []
        self.__start_timestamp = None
        self.__total_load_time = None

    def start(self):
        self.__start_timestamp = self.__driver.execute_script("return new Date().getTime()")

    def mark_measurement_point(self, url):
        if self.__start_timestamp is None:
            raise Exception('mark_measurement_point called before start')

        timing = self.__driver.execute_script("return window.performance.timing")

        self.__measurements.append({
            'url': url,
            'backend_time': timing['responseStart'] - timing['navigationStart'],
            'frontend_time': timing['loadEventEnd'] - timing['responseStart'],
            'total_load_time': timing['loadEventEnd'] - timing['navigationStart'],
            'response_receiving_time': timing['responseEnd'] - timing['responseStart'],
            'interactive_time': timing['domInteractive'] - timing['navigationStart'],
            'dom_complete_time': timing['domComplete'] - timing['navigationStart'],
            'dom_content_loaded_time': timing['domContentLoadedEventEnd'] - timing['navigationStart']
        })

        self.__total_load_time = timing['loadEventEnd'] - self.__start_timestamp

    def get_result(self):
        if len(self.__measurements) == 0:
            return None

        return {
            'total_load_time': self.__total_load_time,
            'steps': self.__measurements
        }
