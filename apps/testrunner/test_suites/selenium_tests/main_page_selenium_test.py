# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from selenium.webdriver.common.keys import Keys
from common.media_wiki import MWUrlGenerator
from testrunner.test_suites.selenium_tests.selenium_test import SeleniumTest

logger = logging.getLogger(__name__)

class MainPageSeleniumTest(SeleniumTest):
    def do_run(self, driver, timer):
        self.measure_page_load(self.baseUrl, driver, timer)

    def __init__(self):
        self.baseUrl = MWUrlGenerator.get_wiki_base_url('synth1', 'muppet') #TODO move hostname
