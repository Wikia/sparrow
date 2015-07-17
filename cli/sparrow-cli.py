#!/usr/bin/env python
"""
Usage:
    sparrow-cli.py [ --server=<server> ] [ --debug ] list
"""
import os
import docopt
import re
import requests
from termcolor import colored


class SparrowCommandLineClient(object):
    RE_ABSOLUTE_URL = re.compile(r'^https?:', re.I)

    def __init__(self, arguments):
        self.arguments = arguments
        self.server = self.arguments['--server'] or os.environ.get('SPARROW_API_SERVER_URL')
        self.debug_flag = arguments['--debug']

    def debug(self, s):
        if self.debug_flag:
            print colored('DEBUG: ' + s, 'blue')

    def api_get_json(self, api_path_or_url):
        if self.RE_ABSOLUTE_URL.match(api_path_or_url):
            url = api_path_or_url
        else:
            url = self.server.rstrip('/') + '/api/v1/' + api_path_or_url.lstrip('/')

        self.debug('HTTP request: ' + url)

        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def run(self):
        self.list_tests()

    def list_tests(self):
        url = '/test_runs/'
        while url:
            response = self.api_get_json(url)
            for test_run in response['results']:
                self.print_test_run(test_run)
            url = response['next']

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


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    SparrowCommandLineClient(arguments).run()
