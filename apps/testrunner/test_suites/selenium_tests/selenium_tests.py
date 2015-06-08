# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from testrunner.test_suites.selenium_tests import selenium_steps
from testrunner.test_suites.selenium_tests import selenium_steps_oasis

logger = logging.getLogger(__name__)


def enter_page(driver, timer, params):
    url = params['url']

    selenium_steps.enter_page(driver, timer, url)


def perftest_oasis_anon_search_pageviews(driver, timer, params):
    hostname = params['hostname']
    perftest_wiki_domain = 'http://perftest.{0}'.format(hostname)

    selenium_steps.enter_page(driver, timer, perftest_wiki_domain + '/wiki/Perftest_Wiki?noexternals=1')
    selenium_steps_oasis.search(driver, timer, 'Big Article')
    selenium_steps.enter_page(driver, timer, perftest_wiki_domain + '/wiki/Big_Article?noexternals=1')
    selenium_steps.enter_page(driver, timer, perftest_wiki_domain + '/wiki/Article_with_few_images?noexternals=1')


def perftest_oasis_user_search_pageviews(driver, timer, params):
    hostname = params['hostname']
    perftest_wiki_domain = 'http://perftest.{0}'.format(hostname)

    selenium_steps.enter_page(driver, timer, perftest_wiki_domain + '/wiki/Perftest_Wiki?noexternals=1')
    selenium_steps.enter_page(driver, timer, perftest_wiki_domain + '/wiki/Special:UserLogin?noexternals=1')
    selenium_steps_oasis.login_on_special_user_login(driver, timer)
    selenium_steps_oasis.search(driver, timer, 'Big Article')
    selenium_steps.enter_page(driver, timer, perftest_wiki_domain + '/wiki/Big_Article?noexternals=1')
    selenium_steps.enter_page(driver, timer, perftest_wiki_domain + '/wiki/Article_with_few_images?noexternals=1')