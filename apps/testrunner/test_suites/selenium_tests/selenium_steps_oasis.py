# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from testrunner.test_suites.selenium_tests import selenium_steps

logger = logging.getLogger(__name__)


def search(driver, timer, text):
    timer.mark_page_load_start(driver.current_url)
    driver.find_element_by_id('searchInput').send_keys(text)
    driver.find_element_by_id('searchSubmit').submit()
    selenium_steps.wait_for_page_load(driver)
    timer.mark_page_load_end(driver.current_url)

def login_on_special_user_login(driver, timer):
    timer.mark_page_load_start(driver.current_url)
    driver.find_element_by_css_selector('.WikiaArticle input[name="username"]').send_keys('keynote')
    driver.find_element_by_css_selector('.WikiaArticle input[name="password"]').send_keys('testme')
    driver.find_element_by_css_selector('.login-button.big').click()
    selenium_steps.wait_for_page_load(driver)
    timer.mark_page_load_end(driver.current_url)