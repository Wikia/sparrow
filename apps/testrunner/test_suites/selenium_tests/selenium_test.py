# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from testrunner.test_suites.selenium_tests.selenium_timer import SeleniumTimer

logger = logging.getLogger(__name__)

class SeleniumTest(object):
    def get_driver(self):
        caps = DesiredCapabilities.CHROME
        #caps['loggingPrefs'] = {'performance': 'ALL'}
        driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver',
                                  service_args=["--verbose", "--log-path=chromelog.log"],
                                  desired_capabilities=caps)

        return driver

    def get_and_measure(self, url, driver, timer):

        driver.get(url)
        self.wait_for_page_load(driver)
        timer.mark_measurement_point(url)

    def wait_for_page_load(self, driver):

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[@title="VisualDNA Analytics"]')))

    def run(self):
        result = None
        try:
            driver = self.get_driver()

            timer = SeleniumTimer(driver)
            timer.start()

            self.do_run(driver, timer)

            #perf = driver.get_log('performance')

            result = timer.get_result()
        except:
            logger.error('Exception caught while running selenium tests', exc_info=True)
        finally:
            driver.quit()

        return result
