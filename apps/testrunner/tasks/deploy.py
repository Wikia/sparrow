# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from contextlib import closing

from testrunner import app as celery_app
from testrunner.ssh import SSHConnection


class Deploy(celery_app.Task):
    def run(self, deploy_host, app, env, repos):
        with closing(SSHConnection(deploy_host)) as connection:
            self.run_prep(connection, app, env, repos)
            self.run_push(connection, app, env)

    @classmethod
    def run_prep(cls, connection, app, env, repos):
        repo_spec = ' '.join([
            '-r {repo_name}@{repo_commit}'.format(repo_name=repo_name, repo_commit=repo_commit)
            for repo_name, repo_commit in repos.items()
        ])

        cmd = 'dt --boring -y prep -a {app} -e {env} {repo_spec}'.format(
            app=app,
            env=env,
            repo_spec=repo_spec
        )

        cls.run_remote_command(connection, cmd)

    @classmethod
    def run_push(cls, connection, app, env):
        cmd = 'dt --boring -y push -a {app} -e {env}'.format(
            app=app,
            env=env
        )

        cls.run_remote_command(connection, cmd)

    @staticmethod
    def run_remote_command(connection, cmd):
        status, stdout, stderr = connection.execute(cmd)

        if status != 0:
            raise RuntimeError('Remote command execution failed.',
                               cmd,
                               status,
                               stdout.getvalue(),
                               stderr.getvalue())