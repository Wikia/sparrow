# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)

class SeleniumTimer(object):

    def __init__(self, driver):
        self.driver = driver
        self.measurements = []

    def start(self, test_name):
        self.start_timestamp = self.driver.execute_script("return new Date().getTime()")
        self.test_name = test_name

    def mark_measurement_point(self, url):
        timing = self.driver.execute_script("return window.performance.timing")

        self.measurements.append(dict(
            url = url,
            backend_time = timing['responseStart'] - timing['navigationStart'],
            frontend_time = timing['loadEventEnd'] - timing['responseStart'],
            total_load_time = timing['loadEventEnd'] - timing['navigationStart'],
            response_receiving_time = timing['responseEnd'] - timing['responseStart'],
            interactive_time = timing['domInteractive'] - timing['navigationStart'],
            dom_complete_time = timing['domComplete'] - timing['navigationStart'],
            dom_content_loaded_time = timing['domContentLoadedEventEnd'] - timing['navigationStart']
        ))

        self.total_load_time = timing['loadEventEnd'] - self.start_timestamp

    def get_result(self):
        if len(self.measurements) == 0:
            return None

        return dict(
            total_load_time = self.total_load_time,
            test_name = self.test_name,
            steps = self.measurements
        )
