# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from . import Action

logger = logging.getLogger(__name__)


class RunSeleniumTest(Action):

    def run(self, selenium_test):
        result = selenium_test.run()

        if result is not None:
            self.status = self.COMPLETED
            self.result = result
        else:
            self.status = self.FAILED