from django.core.management.base import BaseCommand, CommandError
from ...runner import TaskQueueWorker

class Command(BaseCommand):
    help = 'Test runner'

    # def add_arguments(self, parser):
    #     parser.add_argument('test_id', nargs='+', type=int)

    def handle(self, *args, **options):
        test_runner = TaskQueueWorker()
        test_runner.run()
        for test_id in options['test_id']:
            self.stdout.write('Test = {}'.format(test_id))
            # try:
            #     poll = Poll.objects.get(pk=poll_id)
            # except Poll.DoesNotExist:
            #     raise CommandError('Poll "%s" does not exist' % poll_id)
            #
            # poll.opened = False
            # poll.save()
            #
            # self.stdout.write('Successfully closed poll "%s"' % poll_id)