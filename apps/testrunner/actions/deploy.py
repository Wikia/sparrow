# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import Action
from testrunner.ssh import SSHConnection


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