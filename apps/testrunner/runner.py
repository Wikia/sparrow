from .logger import logger
from .tasks import Task, Deploy, HttpGet

class SimpleTest(Task):
    class Config:
        DEPLOY_HOST = 'deploy-s3'
        TARGET_ENV = 'dev-synth1'

    def run(self):
        task_id = self.params['id']
        logger.info('Started execution of task #{}'.format(task_id))

        logger.info('Running deploy task...')
        deploy_task = Deploy(
            deploy_host=self.Config.DEPLOY_HOST,
            app='wikia',
            env=self.Config.TARGET_ENV,
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
