from django.core.management.base import BaseCommand, CommandError

from ...runner import TaskQueueWorker, Task
from ...logger import logger


class FakeTaskRepo(object):
    ACQUIRE = 'acquire'
    RELEASE = 'release'
    SUBMIT_RESULT = 'submit_result'

    def __init__(self, queue, test_case):
        self.queue = list(reversed(queue))
        self.test_case = test_case

    def acquire(self):
        if self.test_case == self.ACQUIRE:
            raise RuntimeError('Test error')
        if len(self.queue) > 0:
            task = self.queue.pop()
            task.repo = self
            return task

    def release(self, task):
        if self.test_case == self.RELEASE:
            raise RuntimeError('Test error')
        logger.info('FakeTestRepo received request to release task #{}'.format(task.id))

    def submit_result(self, task, result):
        if self.test_case == self.SUBMIT_RESULT:
            raise RuntimeError('Test error')
        logger.info('FakeTestRepo received result for task #{}: {}'.format(task.id, result))


class Command(BaseCommand):
    help = 'Run queue consumer with fake task repo'

    def add_arguments(self, parser):
        parser.add_argument('--case', type=str)

    # def add_arguments(self, parser):
    # parser.add_argument('test_id', nargs='+', type=int)

    def handle(self, *args, **options):
        test_case = options['case']

        repo = FakeTaskRepo([Task(None, {
            'id': 1,
            'app_commit': 'dev',
            'config_commit': 'dev',
            'url': 'http://muppet.synth1.wikia-dev.com/wiki/Special:Version',
        })],test_case)
        task_consumer = TaskQueueWorker(repo)
        task_consumer.run()
