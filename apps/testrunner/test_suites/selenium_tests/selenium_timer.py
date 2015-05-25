# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)

class SeleniumTimer(object):

    def __init__(self, driver):
        self.driver = driver
        self.measurements = []

    def start(self):
        self.start_timestamp = self.driver.execute_script("return new Date().getTime()")

    def mark_measurement_point(self, url):
        navigation_start = self.driver.execute_script("return window.performance.timing.navigationStart")
        response_start = self.driver.execute_script("return window.performance.timing.responseStart")
        response_end = self.driver.execute_script("return window.performance.timing.responseEnd")
        dom_interactive = self.driver.execute_script("return window.performance.timing.domInteractive")
        dom_complete = self.driver.execute_script("return window.performance.timing.domComplete")
        dom_content_loaded_event_end = self.driver.execute_script("return window.performance.timing.domContentLoadedEventEnd")
        load_event_end = self.driver.execute_script("return window.performance.timing.loadEventEnd")

        self.measurements.append(dict(
            url = url,
            backend_time = response_start - navigation_start,
            frontendTime = load_event_end - response_start,
            totalLoadTime = load_event_end - navigation_start,
            response_receiving_time = response_end - response_start,
            interactive_time = dom_interactive - navigation_start,
            dom_complete_time = dom_complete - navigation_start,
            dom_content_loaded_time = dom_content_loaded_event_end - navigation_start
        ))

        self.total_load_time = load_event_end - self.start_timestamp

    def get_result(self):
        if len(self.measurements) == 0:
            return None

        return dict(
            total_load_time = self.total_load_time,
            measurements = self.measurements
        )
