# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from phantomas import Phantomas

from . import Action


logger = logging.getLogger(__name__)


class PhantomasRun(Action):
    REQUIRED_PARAMS = (
        'url',
    )

    def __init__(self, *args, **kwargs):
        super(PhantomasRun, self).__init__(*args, **kwargs)

    def run(self):
        try:
            phantomas_runner = Phantomas(
                url=self.params['url']
            )
            phantomas_result = phantomas_runner.run()
            self.result[self._RESULT_NAME].append({
                'generator': phantomas_result._generator,
                'metrics': phantomas_result._metrics,
                'offenders': phantomas_result._offenders
            })
        except:
            logger.error('phantomas execution failed', exc_info=True)

        if len(self.result[self._RESULT_NAME]):
            self.status = self.COMPLETED
        else:
            self.status = self.FAILED

