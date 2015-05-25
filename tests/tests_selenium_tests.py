# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.test import APITestCase
from testrunner.actions.run_selenium_test import RunSeleniumTest
from testrunner.test_suites.selenium_tests.main_page_selenium_test import MainPageSeleniumTest


class TestResultTestCase(APITestCase):
    def setUp(self):
        pass

    #This test requires starting a browser and takes around 10 seconds to invoke, so skipping by default
    def __test_run_test(self):

        simple_selenium_test = MainPageSeleniumTest()
        run_selenium_test_action = RunSeleniumTest()
        run_selenium_test_action.run(simple_selenium_test)

        self.assertTrue(run_selenium_test_action.ok)
