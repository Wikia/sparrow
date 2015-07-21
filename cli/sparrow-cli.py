#!/usr/bin/env python
"""
Usage:
    sparrow-cli.py [ --server=<server> ] [ --debug ]
            ( list |
              compare [ --drop-min-max=<drop_min_max> ] [ --drop-first=<drop_first> ] |
              show <test_run_id> |
              query <test_run_id> <metric_name> )
"""
import csv
import os
import pprint
import urlparse
import logging
import docopt
import re
import requests
from termcolor import colored
import ujson
from metrics import Collection
from metrics.queries import Query
from metrics.values import Stats

logging.basicConfig()
logger = logging.getLogger(__name__)

APP_NAMES = {
    "cd79c90c400985378d32648811fcd70476eb916f": "performance-test-normal",
    "4700207840ffea142e7ee80866c50cf83d63742b": "performance-test-backend-delay-50",
    "05e139282102a51f85e9d0af8843481be50a9439": "performance-test-backend-delay-100",
    "ad570fba29c821e99386af95eafc46d6a6df6fae": "performance-test-backend-delay-200",
    "a9a8e024e5dd09b4ce8a0ed08c2d9f71de6236ed": "performance-test-frontend-delay-50",
    "aea42378779c14ba95bb5d23f2215b261e5e1fec": "performance-test-frontend-delay-100",
    "9273ed4b00845d5a2ae1e33da8125787894f422b": "performance-test-frontend-delay-200",
}

class ObjectCache(object):
    def get(self, name, retrieve_fn, args=None, kwargs=None):
        try:
            data = self.read(name)
        except:
            data = None
        if data is None:
            data = retrieve_fn(*args, **kwargs)
            self.write(name, data)
        return data

class ObjectDiskCache(ObjectCache):
    def __init__(self, dir):
        super(ObjectDiskCache, self).__init__()
        self.dir = dir

    def read(self, name):
        file_name = os.path.join(self.dir, name)
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as f:
                return ujson.load(f)
        return None

    def write(self, name, data):
        file_name = os.path.join(self.dir, name)
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)
        with open(file_name, 'wb') as f:
            ujson.dump(data, f)


class ObjectMemoryCache(ObjectCache):
    def __init__(self, dir):
        super(ObjectMemoryCache, self).__init__()
        self.objects = {}

    def read(self, name):
        return self.objects.get(name)

    def write(self, name, data):
        self.objects[name] = data

class SparrowApiWrapper(object):
    RE_ABSOLUTE_URL = re.compile(r'^https?:', re.I)

    def __init__(self, api_url, cache_dir=None):
        self.api_url = api_url

        if cache_dir is None:
            self.cache = ObjectMemoryCache()
        else:
            self.cache = ObjectDiskCache(cache_dir)

    def request_get_json(self, api_path_or_url):
        if self.RE_ABSOLUTE_URL.match(api_path_or_url):
            url = api_path_or_url
        else:
            url = self.api_url.rstrip('/') + '/api/v1/' + api_path_or_url.lstrip('/')

        logger.debug('HTTP request: ' + url)

        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def iter_test_runs(self):
        url = '/test_runs/'
        while url:
            response = self.request_get_json(url)
            for test_run in response['results']:
                yield test_run
            url = response['next']

    def __extract_object_id(self, url, object_class):
        m = re.search(r'/{}s/([0-9]+)/'.format(object_class), url)
        if not m:
            raise ValueError('Could not extract {} ID from: {}'.format(object_class, url))
        id = int(m.group(1))
        object_id = '{}-{}'.format(object_class, id)
        return object_id

    def get_result(self, url):
        object_id = self.__extract_object_id(url, 'result')
        return self.cache.get(object_id, self.request_get_json, [url])

    def get_test_run(self, url):
        object_id = self.__extract_object_id(url, 'test_run')
        return self.cache.get(object_id, self.request_get_json, [url])


class SparrowCommandLineClient(object):
    RE_ABSOLUTE_URL = re.compile(r'^https?:', re.I)

    def __init__(self, arguments, routes):
        self.arguments = arguments
        self.routes = routes

        self.debug_flag = arguments['--debug']
        if self.debug_flag:
            logging.root.setLevel(logging.DEBUG)

        api_url = self.arguments['--server'] or os.environ.get('SPARROW_API_SERVER_URL')
        cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        self.api = SparrowApiWrapper(api_url, cache_dir)

    def debug(self, s):
        if self.debug_flag:
            print colored('DEBUG: ' + s, 'blue')

    def run(self):
        # print self.arguments
        for option, cls in self.routes.items():
            if self.arguments[option]:
                o = cls(arguments, self.api, self)
                o.execute()



class SparrowCommand(object):
    def __init__(self, arguments, api, cli):
        self.arguments = arguments
        self.api = api
        self.cli = cli

class TestListCommand(SparrowCommand):
    def execute(self):
        for test_run in self.api.iter_test_runs():
            self.print_test_run(test_run)

    def print_test_run(self, test_run):
        tasks = test_run['tasks']
        results = test_run['results']
        color_status = None
        if len(results) > 0:
            color_status = 'green'
        else:
            color_status = 'yellow'

        def print_color(s):
            print colored(s, color_status)

        indent = '      '
        print_color(
            '#{:4} {} app@{} config@{}'.format(test_run['id'], test_run['test_run_uri'], test_run['main_revision'],
                                               test_run['secondary_revision']))
        print_color(indent + '{} tasks, {} results'.format(len(tasks), len(results)))
        for task_url in tasks:
            print_color(indent + 'TASK   {}'.format(task_url))
        for result_url in results:
            print_color(indent + 'RESULT {}'.format(result_url))

class TestShowCommand(SparrowCommand):
    def execute(self):
        test_run_id = int(arguments['<test_run_id>'])

        response = self.api.get_test_run('/test_runs/{}/'.format(test_run_id))
        # response = self.api_get_json('/test_runs/{}/'.format(test_run_id))
        for result_url in response['results']:
            result_item = self.api.get_result(result_url)
            # result_item = self.api_get_json(result_url)
            result = result_item['results']
            metrics = Collection.unserialize(result)
            pprint.pprint(metrics)

class CompareCommand(SparrowCommand):
    def execute(self):
        all_tests = self.get_all_tests()

        urls = set([test['url'] for test in all_tests])
        apps = set([test['app'] for test in all_tests])

        selected_url = min(urls)

        print len(all_tests), len(urls), len(apps)

        # tests = filter(lambda x: x['url'] == selected_url, all_tests)
        tests = all_tests
        for test in tests:
            self.write_csv(APP_NAMES[test['app']], test['url'], test['metrics'])

    def get_all_tests(self):
        tests = []
        for test_run_item in self.api.iter_test_runs():
            test = {
                'url': test_run_item['test_run_uri'],
                'app': test_run_item['main_revision'],
                'config': test_run_item['secondary_revision'],
                'metrics': None
            }
            for result_url in test_run_item['results']:
                result_item = self.api.get_result(result_url)
                test['metrics'] = Collection.unserialize(result_item['results'])
            tests.append(test)
        return tests

    def write_csv(self, name, url, collection):
        def is_skipped_metric(metric):
            id = metric.context['id']
            return id.endswith('.list') or id.endswith('.jQueryVersion') or id.endswith('.statusCodesTrail')

        file_name_suffix = ''
        drop_first = 0
        drop_min_max = 0
        if self.arguments['--drop-first']:
            drop_first = int(self.arguments['--drop-first'])
            file_name_suffix += '-dropfirst-{}'.format(drop_first)
        if self.arguments['--drop-min-max']:
            drop_min_max = int(self.arguments['--drop-min-max'])
            file_name_suffix += '-dropminmax-{}'.format(drop_min_max)
        values_count = 25 - drop_first - 2 * drop_min_max

        header = ['ID',
                  'stddev/mean',
                  'mean',
                  'stddev',
                  'min',
                  'max',
                  'pct_5',
                  'pct_50',
                  'pct_95'] + [''] * values_count
        rows = []
        sorted_metrics = sorted(
            [('{}/{}'.format(metric.context['origin'], metric.context['id']), metric) for metric in
             collection.metrics if not is_skipped_metric(metric)], key=lambda kv: kv[0])
        for id, metric in sorted_metrics:

            raw_values = metric.values.raw_values
            e_values = [{'id': i, 'value': raw_values[i]} for i in range(len(raw_values))]
            if drop_first:
                e_values = e_values[drop_first:]
            e_values = sorted(e_values, key=lambda x: x['value'])
            if drop_min_max:
                e_values = e_values[drop_min_max:-drop_min_max]
            e_values = sorted(e_values, key=lambda x: x['id'])
            raw_values = [x['value'] for x in e_values]

            row = [id]
            try:
                # stats = metric.values.stats
                stats = Stats(raw_values)
                row += ['{:.3f}'.format(stats.stddev / stats.mean if stats.mean != 0 else 0.0).replace('.', ','),
                        stats.mean,
                        stats.stddev,
                        stats.min,
                        stats.max,
                        stats.pct_5,
                        stats.pct_50,
                        stats.pct_95]
            except:
                row += [''] * 7

            row += raw_values
            row = [(v if type(v) is not float else '{}'.format(v).replace('.', ',')) for v in row]
            rows.append(row)

        url = url[url.find('/wiki/') + 6:]
        article, sep, query = url.partition('?')
        qs = urlparse.parse_qs(query)
        file_name = name + '-' + article + ''.join(['-' + k for k in qs.keys()]) + file_name_suffix + '.csv'
        print file_name
        with open(file_name, 'wb') as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        print '========'

class QueryCommand(SparrowCommand):
    def execute(self):
        test_run_ids = sorted(list(parse_ranges(arguments['<test_run_id>'])))
        metric_name = arguments['<metric_name>']

        for test_run_id in test_run_ids:
            print 'TEST RUN', test_run_id
            test_run = self.api.get_test_run('/test_runs/{}/'.format(test_run_id))
            result_url = test_run['results'][0]
            result = self.api.get_result(result_url)
            result_data = result['results']
            collection = Collection.unserialize(result_data)
            print 'RESULT', result_url

            for metric in collection:
                if metric.id == metric_name:
                    raw_values = metric.values.raw_values
                    stats = Stats(raw_values)
                    print metric.context
                    print stats.mean, stats.median
                    print ', '.join(['{}'.format(x) for x in raw_values])

def parse_ranges(s):
    if not s:
        return None

    elements = [e.strip() for e in s.split(',')]
    res = set()
    for element in elements:
        first, sep, second = element.partition('-')
        if second != '':
            res.update(set(range(int(first),int(second)+1)))
        else:
            res.add(int(first))
    return res


ROUTES = {
    'list': TestListCommand,
    'show': TestShowCommand,
    'compare': CompareCommand,
    'query': QueryCommand,
}

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    SparrowCommandLineClient(arguments, ROUTES).run()
