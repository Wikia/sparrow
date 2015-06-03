# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)

def wait_for_page_load(driver):
    driver.implicitly_wait(0.5)
    WebDriverWait(driver, 30).until(lambda d: (d.execute_script('return document.readyState') == 'complete'))
    WebDriverWait(driver, 30).until(lambda d: (d.execute_script('return window.performance.timing.loadEventEnd') > 0))

def enter_page(driver, timer, url):
    timer.mark_page_load_start(url)
    driver.get(url)
    wait_for_page_load(driver)
    timer.mark_page_load_end(url)