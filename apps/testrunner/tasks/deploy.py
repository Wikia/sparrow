# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from contextlib import closing

from celery.utils.log import get_task_logger

from testrunner import app as celery_app
from testrunner.ssh import SSHConnection

logger = get_task_logger(__name__)


class Deploy(celery_app.Task):
    PACKAGE_DIR = '/data/deploytools/packages/wikia/'
    PACKAGE_EXT = '.tar.gz'
    DEPLOY_DIR = '/usr/wikia/source/deploytools/'

    def run(self, deploy_host, app, env, repos):
        with closing(SSHConnection(deploy_host)) as connection:
            self.run_sync(connection, repos)
            self.run_prep(connection, app, env, repos)
            self.run_push(connection, app, env)
        with closing(SSHConnection(env)) as connection:
            self.clean_up_old_releases(env, connection)

    @classmethod
    def run_sync(cls, connection, repos):
        for repo_name, repo_commit in repos.items():
            cmd = 'dt --boring git-sync -r {repo_name}'.format(repo_name=repo_name)
            cls.run_remote_command(connection, cmd)

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

    @classmethod
    def clean_up_old_releases(cls, hostname, connection):
        current_release = int(cls.get_remote_output(connection, 'readlink {}current'.format(cls.DEPLOY_DIR)))
        current_release_str = str(current_release)
        logger.debug('{}: current_release = {}'.format(hostname, current_release))

        deployed_releases = cls.get_remote_output(connection, 'ls {}'.format(cls.DEPLOY_DIR)).split()
        logger.debug('{}: deployed_releases = {}'.format(hostname, deployed_releases))

        for f in deployed_releases:
            if f == 'current' or f == current_release_str or f.startswith('.'):
                continue
            logger.debug('{}: removing deployed release {}'.format(hostname, f))
            cls.run_remote_command(connection, 'rm -rf {}{}'.format(cls.DEPLOY_DIR, f))

        packages = cls.get_remote_output(connection, 'ls {}'.format(cls.PACKAGE_DIR)).split()
        logger.debug('{}: packages = {}'.format(hostname, packages))

        for f in packages:
            if f.startswith('.') or not f.endswith(cls.PACKAGE_EXT):
                continue
            p = f[:len(f) - len(cls.PACKAGE_EXT)]
            app, sep, release = p.rpartition('-')
            release = int(release)
            logger.debug('{}: package file {}: release = {}'.format(hostname, f, release))
            if release == current_release:
                continue
            logger.debug('{}: removing package {}'.format(hostname, f))
            cls.run_remote_command(connection, 'rm {}{}'.format(cls.PACKAGE_DIR, f))

    @classmethod
    def get_remote_output(cls, connection, cmd):
        return cls.run_remote_command(connection, cmd)[0].strip()

    @staticmethod
    def run_remote_command(connection, cmd):
        status, stdout, stderr = connection.execute(cmd)

        if status != 0:
            raise RuntimeError('Remote command execution failed.', cmd, status, stdout, stderr)

        return (stdout, stderr)
