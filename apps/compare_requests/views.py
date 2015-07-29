# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import ujson

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .serializers import CompareRequestSerializer, CreateCompareRequestSerializer
from .models import CompareRequest
from test_runs.models import TestRun

from common.github_integration import GitHub

APP_TARGET_BRANCH = 'dev'
CONFIG_REPO = 'Wikia/config'
CONFIG_BRANCH = 'dev'
COMPARE_URL = 'http://muppet.synth1.wikia-dev.com/wiki/Kermit?noexternals=1'

logger = logging.getLogger(__name__)


def find_or_create_test_run(url, name, app_commit, config_commit):
    logger.debug('Searching for test run: url={} app_commit={} config_commit={}'.format(
        url, app_commit, config_commit
    ))
    possible_test_runs = TestRun.objects.filter(
        test_run_uri=url,
        main_revision=app_commit,
        secondary_revision=config_commit,
    ).order_by('-created')
    test_run = possible_test_runs[0:1]
    if len(test_run) == 0:
        logger.debug('  not found, creating new one...')
        test_run = TestRun(
            test_run_uri=url,
            name=name,
            main_revision=app_commit,
            secondary_revision=config_commit,
        )
        test_run.save_and_run()
        logger.debug('Created TestRun.id = {}'.format(test_run.id))
    else:
        test_run = test_run[0]
        logger.debug('  found! TestRun.id = {}'.format(test_run.id))
    return test_run


def create_test_run(url, name, app_commit, config_commit):
    logger.debug('Creating test run...')
    test_run = TestRun(
        test_run_uri=url,
        name=name,
        main_revision=app_commit,
        secondary_revision=config_commit,
    )
    test_run.save_and_run()
    logger.debug('Created TestRun.id = {}'.format(test_run.id))
    return test_run


class CompareRequestViewSet(viewsets.ModelViewSet):
    queryset = CompareRequest.objects.all()
    serializer_class = CompareRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateCompareRequestSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        repo_name = serializer.data['repo']
        pull_req_num = serializer.data['pull_request_num']

        github = GitHub()

        logger.debug('Querying pull request info: {}/{}'.format(repo_name, pull_req_num))
        pull_info = github.get_pull_request_info(repo_name, pull_req_num)
        logger.debug('  received: {}'.format(ujson.dumps(pull_info)))

        app_branch_info = pull_info['head']
        logger.debug('Querying branch info: {} : {}'.format(repo_name, pull_info['base']['ref']))
        app_dev_info = github.get_branch_info(repo_name, APP_TARGET_BRANCH)['head']
        logger.debug('  received: {}'.format(ujson.dumps(app_branch_info)))

        logger.debug('Searching for existing compare requests for: head_sha={} base_sha={}'.format(
            app_branch_info['sha'], app_dev_info['sha']))
        existing_requests = CompareRequest.objects.filter(
            head_sha=app_branch_info['sha'],
            base_sha=app_dev_info['sha']
        ).order_by('-created')[0:1]

        if len(existing_requests) == 1:
            compare_request = existing_requests[0]
            logger.debug('  found! CompareRequest.id = {}'.format(compare_request.id))
            status_code = status.HTTP_200_OK
        else:
            logger.debug('  not found, creating new one...')

            app_merged_branch_name = 'sparrow-test-{}-{}'.format(app_branch_info['sha'], app_dev_info['sha'])
            logger.debug('Creating merged branch: {}'.format(app_merged_branch_name))
            try:
                app_merged_info = github.create_merged_ref(repo_name, app_merged_branch_name, app_branch_info['sha'],
                                                              APP_TARGET_BRANCH)
            except:
                # assume the branch has been correctly created by another process
                app_merged_info = github.get_branch_info(repo_name, app_merged_branch_name)

            app_merged_info = app_merged_info['head']
            logger.debug('  received: {}'.format(ujson.dumps(app_merged_info)))

            logger.debug('Querying branch info: {} : {}'.format(CONFIG_REPO, CONFIG_BRANCH))
            config_dev_info = github.get_branch_info(CONFIG_REPO, CONFIG_BRANCH)['head']
            logger.debug('  received: {}'.format(ujson.dumps(config_dev_info)))

            compare_request = CompareRequest()
            compare_request.repo = repo_name
            compare_request.pull_request_num = pull_req_num

            compare_request.head_ref = app_branch_info['ref']
            compare_request.head_sha = app_merged_info['sha']
            compare_request.head_test_run = create_test_run(COMPARE_URL,
                                                            app_branch_info['ref'],
                                                            app_merged_info['sha'],
                                                            config_dev_info['sha'])

            compare_request.base_ref = app_dev_info['ref']
            compare_request.base_sha = app_dev_info['sha']
            compare_request.base_test_run = create_test_run(COMPARE_URL,
                                                            app_dev_info['ref'],
                                                            app_dev_info['sha'],
                                                            config_dev_info['sha'])

            compare_request.save()
            logger.debug('Created CompareRequest.id = {}'.format(compare_request.id))
            status_code = status.HTTP_201_CREATED

        serializer = CompareRequestSerializer(compare_request, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status_code, headers=headers)
