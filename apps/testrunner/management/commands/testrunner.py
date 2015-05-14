from django.core.management.base import BaseCommand
from ...runner import TaskQueueWorker


class Command(BaseCommand):
    help = 'Test runner'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemonize', '-d',
            action='store_true',
            dest='daemonize'
        )

    def handle(self, *args, **options):
        test_runner = TaskQueueWorker()
        test_runner.run(daemonize=options['daemonize'])
