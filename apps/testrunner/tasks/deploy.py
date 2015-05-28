# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from testrunner import app as celery_app
from testrunner.ssh import SSHConnection


class Deploy(celery_app.Task):
    def run(self, deploy_host, app, env, repos):
        try:
            self.ssh_connection = SSHConnection(deploy_host)
            self.run_prep(app, env, repos)
            self.run_push(app, env)
        finally:
            self.ssh_connection.close()

    def run_prep(self, app, env, repos):
        repo_spec = ' '.join([
            '-r {repo_name}@{repo_commit}'.format(repo_name=repo_name, repo_commit=repo_commit)
            for repo_name, repo_commit in repos.items()
        ])

        cmd = 'dt --boring -y prep -a {app} -e {env} {repo_spec}'.format(
            app=app,
            env=env,
            repo_spec=repo_spec
        )

        self.run_remote_command(cmd)

    def run_push(self, app, env):
        cmd = 'dt --boring -y push -a {app} -e {env}'.format(
            app=app,
            env=env
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