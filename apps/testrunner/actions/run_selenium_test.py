# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import namedtuple
from contextlib import closing

import logging

from . import Action
from testrunner.test_suites.selenium_tests.selenium_timer import SeleniumTimer
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from browsermobproxy import Server
from sparrow.settings import base
from testrunner.test_suites.selenium_tests import selenium_tests

logger = logging.getLogger(__name__)


class RunSeleniumTest(Action):
    Test = namedtuple('Test', 'name, params')

    def get_proxy(self):

        server = Server(base.BROWSERMOB_PROXY_PATH)
        server.start()
        proxy = server.create_proxy()

        return proxy

    def get_driver(self, proxy):

        caps = DesiredCapabilities.CHROME
        proxy.add_to_webdriver_capabilities(caps)
        driver = webdriver.Chrome(executable_path=base.CRHOMEDRIVER_PATH,
                                  service_args=["--verbose", "--log-path=chromelog.log"],
                                  desired_capabilities=caps)
        driver.implicitly_wait(1)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)

        return driver

    def run_test(self, test, driver, timer):
        test_func = getattr(selenium_tests, test.name)
        test_func(driver, timer, test.params)


    def run(self, tests):

        result_list = []

        for test in tests:

            logger.info('Running selenium test ' + test.name)
            try:
                with closing(self.get_proxy()) as proxy:
                    with closing(self.get_driver(proxy)) as driver:

                        timer = SeleniumTimer(driver, proxy)
                        timer.start(test.name)

                        self.run_test(test, driver, timer)

                        result_list.append(timer.get_result())
            except:
                logger.error('Exception caught while running selenium test ' + test.name, exc_info=True)

        if len(result_list) > 0:
            self.status = self.COMPLETED
            self.result = {'selenium' : result_list}
        else:
            self.status = self.FAILED
