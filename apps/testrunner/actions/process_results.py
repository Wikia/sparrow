# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy
import logging
import re
import six

from . import Action

logger = logging.getLogger(__name__)


class ProcessResponses(Action):
    REQUIRED_PARAMS = (
        'results',
    )

    __PROFILER_REGEXP = re.compile(r'^\s*([\d\.]+\%)\s+([\d\.]+)\s+(\d+)\s+\-\s+([^\s].*[^\s])\s*$')
    __MEMCACHE_REGEXP = re.compile(r'MWMemcached::get.*!(HIT|MISS|DUPE)')

    def _parse_backend_metrics(self, raw_data):
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
                    metrics['query_time'] += time

                    if name == 'DatabaseBase::query-master':
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

    @staticmethod
    def _calculate_stats(values):
        return {
            'count': int(len(values)),
            '5th_percentile': float(numpy.percentile(values, 5)),
            '50th_percentile': float(numpy.percentile(values, 50)),
            '90th_percentile': float(numpy.percentile(values, 90)),
            '95th_percentile': float(numpy.percentile(values, 95)),
            'std': float(numpy.std(values)),
            'mean': float(numpy.mean(values)),
            'median': float(numpy.median(values)),
            'lowest': float(numpy.min(values)),
            'highest': float(numpy.max(values)),
        }

    def run(self):
        logger.info('Starting processing results')

        response_times = [
            float(response.headers['X-Backend-Response-Time']) for response in self.params['results']['http_get']
        ]

        self.result['response_time'] = self._calculate_stats(response_times)
        self.result['backend_metrics'] = {}

        for response in self.params['results']['mw_profiler_get']:
            start_pos = response.text.rindex('<!--')
            end_pos = response.text.rindex('-->')

            if start_pos < 0 or end_pos < 0:
                logger.warn('Cannot find backend performance metrics')
                continue

            parsed_metrics = self._parse_backend_metrics(response.text[start_pos+4:end_pos])
            for metric, value in six.iteritems(parsed_metrics):
                if metric in self.result['backend_metrics']:
                    self.result['backend_metrics'][metric].append(value)
                else:
                    self.result['backend_metrics'][metric] = [value, ]

        for metric, value in six.iteritems(self.result['backend_metrics']):
            self.result['backend_metrics'][metric] = self._calculate_stats(value)

        self.status = self.COMPLETED
