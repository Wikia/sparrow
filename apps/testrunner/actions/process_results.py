# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy
import logging
import re

from . import Action

logger = logging.getLogger(__name__)


class ProcessResponses(Action):
    REQUIRED_PARAMS = (
        'results',
    )

    __PROFILER_REGEXP = re.compile(r'^\s*([\d\.]+\%)\s+([\d\.]+)\s+(\d+)\s+\-\s+([^\s].*[^\s])\s*$')
    __MEMCACHE_REGEXP = re.compile(r'MWMemcached::get.*!(HIT|MISS|DUPE)')

    def _parse_metrics(self, raw_data):
        metrics = {
            'server_time': 0.0,
            'query_time': 0.0,
            'query_master': 0,
            'query_slave': 0,
            'memc_time': 0.0,
            'memc_misses': 0,
            'memc_hits': 0,
            'memc_dupes': 0
        }

        for line in raw_data.splitlines():
            match = self.__PROFILER_REGEXP.match(line)

            if match is not None:
                (percent, time, count, name) = match.groups()

                percent = float(percent.strip('%'))
                time = float(time)
                count = int(count)

                if name == '-total':
                    metrics['server_time'] += time
                elif name == 'DatabaseBase::query' or name == 'DatabaseBase::query-master':
                    is_master = name == 'DatabaseBase::query-master'
                    metrics['query_time'] += time

                    if is_master:
                        metrics['query_master'] += count
                    else:
                        metrics['query_slave'] += count
                elif name == 'MWMemcached::get':
                    metrics['memc_time'] += time
                else:
                    match = re.match(self.__MEMCACHE_REGEXP, name)

                    if match is not None:
                        memc_type = match.group(1)
                        if memc_type == 'HIT':
                            metrics['memc_hits'] += count
                        elif memc_type == 'MISS':
                            metrics['memc_misses'] += count
                        elif memc_type == 'DUPE':
                            metrics['memc_dupes'] += count
        return metrics

    def run(self):
        logger.info('Starting processing results')

        response_times = [
            float(response.headers['X-Backend-Response-Time']) for response in self.params['results']['http_get']
        ]

        self.result['response_time'] = {
            'mean': numpy.mean(response_times),
            'median': numpy.median(response_times),
            'lowest': numpy.min(response_times),
            'highest': numpy.max(response_times),
        }

        for response in self.params['results']['mw_profiler_get']:
            start_pos = response.text.rindex('<!--')
            end_pos = response.text.rindex('-->')

            if start_pos < 0 or end_pos < 0:
                logger.warn('Cannot find backend performance metrics')
                continue

            self.result['backend'] = self._parse_metrics(response.text[start_pos+4:end_pos])

        self.status = self.COMPLETED
