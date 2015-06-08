# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy
import re
import six
import requests
import ujson
from celery.utils.log import get_task_logger

from testrunner import app as celery_app
from common.utils import camel2snake

logger = get_task_logger(__name__)


class ProcessResponses(celery_app.Task):
    __PROFILER_REGEXP = re.compile(r'^\s*([\d\.]+\%)\s+([\d\.]+)\s+(\d+)\s+\-\s+([^\s].*[^\s])\s*$')
    __MEMCACHE_REGEXP = re.compile(r'MWMemcached::get.*!(HIT|MISS|DUPE)')
    __QUERY_REGEXP = re.compile(r'^\s*query(?:-m)?:\s*(.*)\s*$')

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
        raw_metrics = {
            'queries': [],
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
                    match = self.__MEMCACHE_REGEXP.match(name)

                    if match is not None:
                        memc_type = match.group(1)
                        if memc_type == 'HIT':
                            metrics['memc_hits'] += count
                        elif memc_type == 'MISS':
                            metrics['memc_misses'] += count
                        elif memc_type == 'DUPE':
                            metrics['memc_dupes'] += count

                    match = self.__QUERY_REGEXP.match(name)

                    if match is not None:
                        raw_metrics['queries'].append({
                            'statement': match.group(1),
                            'count': count,
                            'time': time,
                        })

        return {
            'metrics': metrics,
            'raw': raw_metrics,
        }

    @staticmethod
    def _calculate_stats(values):
        if len(values) == 0:
            return {
                'count': 0,
                '5th_percentile': 0.0,
                '50th_percentile': 0.0,
                '90th_percentile': 0.0,
                '95th_percentile': 0.0,
                'std': 0.0,
                'mean': 0.0,
                'median': 0.0,
                'lowest': 0.0,
                'highest': 0.0,
            }

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

    @staticmethod
    def post_results(uri, test_run_uri, task_uri, results):
        logger.info('Saving results')
        payload = {
            'results': results,
            'task': task_uri,
            'test_run': test_run_uri,
        }

        response = requests.post(
            uri,
            data=ujson.dumps(payload),
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json',
            }
        )
        logger.debug('Response (code: {0}): {1}'.format(response.status_code, response.content))
        response.raise_for_status()

    @staticmethod
    def _calculate_selenium_stats_single_step(selenium_results, test_name, metric):
        return ProcessResponses._calculate_stats(
            [x['result']['steps'][0][metric] for x in selenium_results[test_name]])

    @staticmethod
    def _calculate_selenium_stats_total_load_time(selenium_results, test_name, metric):
        return ProcessResponses._calculate_stats(
            [x['result']['total_load_time'] for x in selenium_results[test_name]])

    @staticmethod
    def _get_selenium_metrics(selenium_results):
        result = {}
        result['page_load_no_externals'] = ProcessResponses._calculate_selenium_stats_single_step(
            selenium_results, 'oasis_perftest_medium_article_no_externals', 'total_load_time');
        result['page_dom_complete_no_externals'] = ProcessResponses._calculate_selenium_stats_single_step(
            selenium_results, 'oasis_perftest_medium_article_no_externals', 'dom_complete_time');
        result['page_load_no_ads'] = ProcessResponses._calculate_selenium_stats_single_step(
            selenium_results, 'oasis_perftest_medium_article_no_ads', 'total_load_time');
        result['page_dom_complete_no_ads'] = ProcessResponses._calculate_selenium_stats_single_step(
            selenium_results, 'oasis_perftest_medium_article_no_ads', 'dom_complete_time');
        result['perftest_oasis_anon_search_pageviews_total_load_time'] = ProcessResponses._calculate_selenium_stats_total_load_time(
            selenium_results, 'perftest_oasis_anon_search_pageviews', 'total_load_time');
        result['perftest_oasis_user_search_pageviews_total_load_time'] = ProcessResponses._calculate_selenium_stats_total_load_time(
            selenium_results, 'perftest_oasis_user_search_pageviews', 'total_load_time');

        return result

    def run(self, data, test_run_uri, task_uri, result_uri):
        logger.info('Starting processing results...')

        results = {}
        for item in data:
            if 'http_get' in item:
                logger.info('Gathering HTTP response times...')

                response_times = [
                    float(response['headers']['x-backend-response-time']) for response in item['http_get']
                ]
                results['response_time'] = self._calculate_stats(response_times)
            elif 'mw_profiler_get' in item:
                logger.info('Gathering backend statistics...')

                results['backend_metrics'] = {}
                for response in item['mw_profiler_get']:
                    try:
                        start_pos = response['content'].rindex('<!--')
                        end_pos = response['content'].rindex('-->')
                    except ValueError:
                        logger.warn('Cannot find backend performance metrics')
                        continue

                    metrics = self._parse_backend_metrics(response['content'][start_pos+4:end_pos])
                    # raw_result['backend_metrics'].append(metrics['raw'])
                    for metric, value in six.iteritems(metrics['metrics']):
                        if metric in results['backend_metrics']:
                            results['backend_metrics'][metric].append(value)
                        else:
                            results['backend_metrics'][metric] = [value, ]

                for metric, value in six.iteritems(results['backend_metrics']):
                    results['backend_metrics'][metric] = self._calculate_stats(value)
            elif 'selenium' in item:
                logger.info('Gathering selenium statistics...')

                results['selenium_raw'] = item['selenium']
                results['selenium_metrics'] = self._get_selenium_metrics(item['selenium'])
            elif 'phantomas_get' in item:
                results['phantomas_metrics'] = {}
                phantomas_metrics = [
                    'cssCount', 'imageCount', 'jsCount', 'htmlCount', 'videoCount', 'otherCount',
                    'contentLength', 'bodySize', 'bodyHTMLSize',
                    'cssSize', 'imageSize', 'jsSize', 'htmlSize', 'videoSize', 'otherSize',
                    'ajaxRequests',
                    'DOMqueries', 'DOMinserts', 'DOMelementsCount', 'DOMelementMaxDepth', ]
                for in_name in phantomas_metrics:
                    if in_name.startswith('DOM'):
                        out_name = camel2snake(in_name[:3] + in_name[3].upper() + in_name[4:])
                    else:
                        out_name = camel2snake(in_name)
                    results['phantomas_metrics'][out_name] = self._calculate_stats(
                        [x['metrics'][in_name] for x in item['phantomas_get']]
                    )

        self.post_results(result_uri, test_run_uri, task_uri, results)

