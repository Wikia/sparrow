import requests

from .ssh import SSHConnection


class Task(object):
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = -1

    REQUIRED_PARAMS = []

    def __init__(self, params=None, **kwargs):
        self.status = self.PENDING

        self.params = {}
        self.params.update(params or {})
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


class Deploy(Task):
    REQUIRED_PARAMS = [
        'deploy_host',
        'app',
        'env',
        'repos',
    ]

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


class HttpGet(Task):
    REQUIRED_PARAMS = [
        'url'
    ]

    def run(self):
        response = requests.get(self.params['url'])

        self.result['response'] = response
        if response.ok:
            self.status = self.COMPLETED
        else:
            self.status = self.FAILED
