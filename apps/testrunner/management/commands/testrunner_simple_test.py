import logging
import pprint

from django.core.management.base import BaseCommand
from ...test_suites.simple import SimpleTestSuite

from ...runner import Task


class Command(BaseCommand):
    help = 'Run fake test'

    def add_arguments(self, parser):
        parser.add_argument('--runs', type=int, default=2)

    def handle(self, *args, **options):
        num_runs = options['runs']
        print "Spawning SimpleTestSuite with {} runs...".format(num_runs)
        task = Task(None,{
            'id': 1,
            'app_commit': 'dev',
            'config_commit': 'dev',
            'url': 'http://muppet.synth1.wikia-dev.com/wiki/Special:Version',
            'retries': num_runs
        })
        test_run = SimpleTestSuite(task)
        test_run.run()

        pprint.pprint(test_run.result)
