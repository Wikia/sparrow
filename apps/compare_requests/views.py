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

CONFIG_REPO = 'Wikia/config'
CONFIG_BRANCH = 'dev'
COMPARE_URL = 'http://muppet.synth1.wikia-dev.com/wiki/Kermit'

logger = logging.getLogger(__name__)


def find_or_create_test_run(url, app_commit, config_commit):
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
            main_revision=app_commit,
            secondary_revision=config_commit,
        )
        test_run.save()
        logger.debug('Created TestRun.id = {}'.format(test_run.id))
    else:
        test_run = test_run[0]
        logger.debug('  found! TestRun.id = {}'.format(test_run.id))
    return test_run


def create_test_run(url, app_commit, config_commit):
    logger.debug('Creating test run...')
    test_run = TestRun(
        test_run_uri=url,
        main_revision=app_commit,
        secondary_revision=config_commit,
    )
    test_run.save()
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

        app_head_info = pull_info['head']
        logger.debug('Querying branch info: {} : {}'.format(repo_name, pull_info['base']['ref']))
        app_base_info = github.get_branch_info(repo_name, pull_info['base']['ref'])['head']
        logger.debug('  received: {}'.format(ujson.dumps(app_head_info)))

        logger.debug('Querying branch info: {} : {}'.format(CONFIG_REPO, CONFIG_BRANCH))
        config_info = github.get_branch_info(CONFIG_REPO, CONFIG_BRANCH)['head']
        logger.debug('  received: {}'.format(ujson.dumps(config_info)))

        logger.debug('Searching for existing compare requests for: head_sha={} base_sha={}'.format(
            app_head_info['sha'], app_base_info['sha']))
        existing_requests = CompareRequest.objects.filter(
            head_sha=app_head_info['sha'],
            base_sha=app_base_info['sha']
        ).order_by('-created')[0:1]

        if len(existing_requests) == 1:
            compare_request = existing_requests[0]
            logger.debug('  found! CompareRequest.id = {}'.format(compare_request.id))
            status_code = status.HTTP_200_OK
        else:
            logger.debug('  not found, creating new one...')

            compare_request = CompareRequest()
            compare_request.repo = repo_name
            compare_request.pull_request_num = pull_req_num

            compare_request.head_ref = app_head_info['ref']
            compare_request.head_sha = app_head_info['sha']
            compare_request.head_test_run = create_test_run(COMPARE_URL, app_head_info['ref'],
                                                            config_info['ref'])

            compare_request.base_ref = app_base_info['ref']
            compare_request.base_sha = app_base_info['sha']
            compare_request.base_test_run = create_test_run(COMPARE_URL, app_base_info['ref'],
                                                            config_info['ref'])

            compare_request.save()
            logger.debug('Created CompareRequest.id = {}'.format(compare_request.id))
            status_code = status.HTTP_201_CREATED

        serializer = CompareRequestSerializer(compare_request, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status_code, headers=headers)
