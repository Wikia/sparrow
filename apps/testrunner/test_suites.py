from django.conf import settings
import ujson

from .logger import logger
from .test_actions import Action, Deploy, HttpGet

class SimpleTestSuite(Action):
    def __init__(self, *args, **kwargs):
        super(SimpleTestSuite,self).__init__(*args,**kwargs)
        test_runner_config = settings.SPARROW_TEST_RUNNER
        self.DEPLOY_HOST = test_runner_config['deploy_host']['hostname']
        self.TARGET_ENV = test_runner_config['target_hosts'][0]['hostname']

    def run(self):
        task_id = self.params['id']
        logger.info('Started execution of task #{}'.format(task_id))
        logger.debug('params = ' + ujson.dumps(self.params))

        logger.info('Running deploy task...')
        deploy_task = Deploy(
            deploy_host=self.DEPLOY_HOST,
            app='wikia',
            env=self.TARGET_ENV,
            repos={
                'app': self.params['app_commit'],
                'config': self.params['config_commit']
            })
        deploy_task.run()

        if not deploy_task.ok:
            raise RuntimeError('Could not deploy application')

        logger.info('Running http get task...')
        http_get_task = HttpGet(url=self.params['url'])
        http_get_task.run()

        if not http_get_task.ok:
            raise RuntimeError('Could not perform HTTP request to application')

        logger.info('Fetching response time...')
        http_response = http_get_task.result['response']
        response_time = float(http_response.headers['X-Backend-Response-Time'])

        self.result['response_time'] = response_time
        self.status = self.COMPLETED
        logger.info('Finished execution of task #{}'.format(task_id))
