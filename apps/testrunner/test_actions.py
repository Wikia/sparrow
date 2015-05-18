import requests
import statistics

from .ssh import SSHConnection
import logging

logger = logging.getLogger(__name__)


class Action(object):
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = -1

    REQUIRED_PARAMS = ()

    def __init__(self, params=None, **kwargs):
        self.status = self.PENDING

        self.params = {}
        if params is not None:
            self.params.update(params)
        self.params.update(kwargs)

        self.result = {}

        self.validate_params()

    def validate_params(self):
        for param_name in self.REQUIRED_PARAMS:
            if param_name not in self.params:
                raise KeyError(
                    "{class_name}: Parameter '{parameter}' is required.".format(class_name=self.__class__.__name__,
                                                                                parameter=param_name))

    @property
    def ok(self):
        return self.status == self.COMPLETED

    def run(self):
        raise NotImplementedError('Task.run() is an abstract method.')


class Deploy(Action):
    REQUIRED_PARAMS = (
        'deploy_host',
        'app',
        'env',
        'repos',
    )

    def run(self):
        self.ssh_connection = SSHConnection(self.params['deploy_host'])
        try:
            self.run_prep()
            self.run_push()
            self.status = self.COMPLETED
        except Exception as e:
            self.status = self.FAILED
            raise e
        finally:
            self.ssh_connection.close()

    def run_prep(self):
        repo_spec = ' '.join([
            '-r {repo_name}@{repo_commit}'.format(repo_name=repo_name, repo_commit=repo_commit)
            for repo_name, repo_commit in self.params['repos'].items()
        ])

        cmd = 'dt --boring -y prep -a {app} -e {env} {repo_spec}'.format(
            app=self.params['app'],
            env=self.params['env'],
            repo_spec=repo_spec
        )

        self.run_remote_command(cmd)

    def run_push(self):
        cmd = 'dt --boring -y push -a {app} -e {env}'.format(
            app=self.params['app'],
            env=self.params['env']
        )

        self.run_remote_command(cmd)

    def run_remote_command(self, cmd):
        status, stdout, stderr = self.ssh_connection.execute(cmd)

        if status != 0:
            raise RuntimeError('Remote command execution failed.',
                               cmd,
                               status,
                               stdout.getvalue(),
                               stderr.getvalue())


class HttpGet(Action):
    REQUIRED_PARAMS = (
        'url',
        'retries',
    )

    def run(self):
        self.result['responses'] = []

        for retry in range(1, self.params['retries']+1):
            logger.info('HTTP request #{0} (GET): {1}'.format(retry, self.params['url']))
            response = requests.get(self.params['url'])
            if response.ok:
                logger.debug(
                    'HTTP #{0} response {1}: <full dump skipped> ({2} bytes)'.format(
                        retry, response.status_code, len(response.content)
                    )
                )
            else:
                logger.debug('HTTP #{0} response {1}: {2}'.format(retry, response.status_code, response.content))
                continue

            self.result['responses'].append(response)

        if len(self.result['responses']):
            self.status = self.COMPLETED
        else:
            self.status = self.FAILED

class ProcessResponses(Action):
    REQUIRED_PARAMS = (
        'responses',
    )

    def run(self):
        logger.info('Starting processing {0} results'.format(len(self.params['responses'])))

        metrics = [float(response.headers['X-Backend-Response-Time']) for response in self.params['responses']]
        self.result['response_time'] = {
            'mean': statistics.mean(metrics),
            'median': statistics.median(metrics),
            'lowest': min(metrics),
            'highest': max(metrics),
        }

        self.status = self.COMPLETED
