import logging
import pprint

from django.core.management.base import BaseCommand, CommandError

from ...queue import Task
from ...runner import SimpleTest


class Command(BaseCommand):
    help = 'Run fake test'

    # def add_arguments(self, parser):
    #     parser.add_argument('test_id', nargs='+', type=int)

    def handle(self, *args, **options):
        task = Task(None,1,{
            'app_commit': 'dev',
            'config_commit': 'dev',
            'url': 'http://community.wikia.com/wiki/Special:Version',
        })
        test_run = SimpleTest(task)
        test_run.run()

        pprint.pprint(test_run.get_result().data)
