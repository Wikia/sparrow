import logging
import pprint

from django.core.management.base import BaseCommand, CommandError

from ...runner import Task
from ...test_suites import SimpleTestSuite


class Command(BaseCommand):
    help = 'Run fake test'

    # def add_arguments(self, parser):
    #     parser.add_argument('test_id', nargs='+', type=int)

    def handle(self, *args, **options):
        task = Task(None,{
            'id': 1,
            'app_commit': 'dev',
            'config_commit': 'dev',
            'url': 'http://muppet.synth1.wikia-dev.com/wiki/Special:Version',
        })
        test_run = SimpleTestSuite(task)
        test_run.run()

        pprint.pprint(test_run.result)
