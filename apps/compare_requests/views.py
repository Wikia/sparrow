# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import ujson
from github import GithubException

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from common.utils import cached_property

from .serializers import CompareRequestSerializer, CreateCompareRequestSerializer
from .models import CompareRequest
from test_runs.models import TestRun

from common.github_integration import GitHub, MergeFailed

SHA = 'sha'
REF = 'ref'

APP_TARGET_BRANCH = 'dev'
CONFIG_REPO = 'Wikia/config'
CONFIG_BRANCH = 'dev'
COMPARE_URL = 'http://muppet.synth1.wikia-dev.com/wiki/Kermit?noexternals=1'

logger = logging.getLogger(__name__)


class CompareRequestViewSet(viewsets.ModelViewSet):
    queryset = CompareRequest.objects.all()
    serializer_class = CompareRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateCompareRequestSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        repo_name = serializer.data['repo']
        pull_req_num = serializer.data['pull_request_num']

        github = GitHub()
        create_compare_request = CreateCompareRequest(github, repo_name, pull_req_num)

        try:
            create_compare_request.execute()
        except MergeFailed as e:
            github.post_pull_request_comment(repo_name, pull_req_num, self.get_merge_failed_message())
            raise


        compare_request = create_compare_request.result
        if not create_compare_request.status:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            if create_compare_request.was_created:
                status_code = status.HTTP_201_CREATED
            else:
                status_code = status.HTTP_200_OK

        serializer = CompareRequestSerializer(compare_request, context=self.get_serializer_context())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status_code, headers=headers)

    def get_merge_failed_message(self):
        return ':exclamation: [WikiaSparrow] Could not merge your branch with dev. Please update your branch and request the test again.'

class CreateCompareRequest(object):
    def __init__(self, github, repo_name, pull_req_num):
        self.repo_name = repo_name
        self.pull_req_num = pull_req_num
        self.github = github

        self.status = False
        self.was_created = None
        self.result = None

    def execute(self):
        compare_request = self.find_compare_request(self.app_branch_info[SHA], self.app_dev_info[SHA])

        if compare_request is not None:
            self.was_created = False
        else:
            compare_request = self.create_compare_reqest()
            self.was_created = True

        self.status = True
        self.result = compare_request

    def create_compare_reqest(self):
        logger.debug('Creating Compare request...')

        compare_request = CompareRequest()
        compare_request.repo = self.repo_name
        compare_request.pull_request_num = self.pull_req_num

        compare_request.head_ref = self.app_branch_info[REF]
        compare_request.head_sha = self.app_branch_info[SHA]
        compare_request.head_test_run = self.branch_test_run # branch merged with dev

        compare_request.base_ref = self.app_dev_info[REF]
        compare_request.base_sha = self.app_dev_info[SHA]
        compare_request.base_test_run = self.dev_test_run

        compare_request.save()

        logger.debug('Created CompareRequest.id = {}'.format(compare_request.id))
        return compare_request

    def find_compare_request(self, head_sha, base_sha):
        logger.debug('Searching for existing compare requests for: head_sha={} base_sha={}'.format(
            head_sha, base_sha))
        existing_requests = CompareRequest.objects.filter(
            head_sha=head_sha,
            base_sha=base_sha
        ).order_by('-created')[0:1]

        if len(existing_requests) == 0:
            logger.debug('Compare request not found.')
            return None

        compare_request = existing_requests[0]
        logger.debug('Compare request found! CompareRequest.id = {}'.format(compare_request.id))
        return compare_request


    def find_or_create_test_run(self, url, name, app_commit, config_commit):
        test_run = self.find_test_run(url, name, app_commit, config_commit)

        if test_run is None:
            test_run = self.create_test_run(url, name, app_commit, config_commit)

        return test_run

    def find_test_run(self, url, name, app_commit, config_commit):
        logger.debug('Searching for test run [{}, {}, {}, {}]'.format(
            name, url, app_commit, config_commit
        ))
        possible_test_runs = TestRun.objects.filter(
            name=name,
            test_run_uri=url,
            main_revision=app_commit,
            secondary_revision=config_commit,
        ).order_by('-created')
        test_runs = possible_test_runs[0:1]
        if len(test_runs) == 0:
            logger.debug('Test run not found.')
            return None

        test_run = test_runs[0]
        logger.debug('Test run found! TestRun.id = {}'.format(test_run.id))
        return test_run


    def create_test_run(self, url, name, app_commit, config_commit):
        logger.debug('Creating test run [{}, {}, {}, {}]...'.format(url, name, app_commit, config_commit))
        test_run = TestRun(
            test_run_uri=url,
            name=name,
            main_revision=app_commit,
            secondary_revision=config_commit,
        )
        test_run.save_and_run()
        logger.debug('Created TestRun.id = {}'.format(test_run.id))
        return test_run

    @cached_property
    def pull_info(self):
        logger.debug('Requesting pull request info: {}/#{}'.format(self.repo_name, self.pull_req_num))
        return self.github.get_pull_request_info(self.repo_name, self.pull_req_num)

    @cached_property
    def app_branch_info(self):
        return self.pull_info['head']

    @cached_property
    def app_dev_info(self):
        logger.debug('Requesting app branch info: {}/{}'.format(self.repo_name, APP_TARGET_BRANCH))
        return self.github.get_branch_info(self.repo_name, APP_TARGET_BRANCH)['head']

    @cached_property
    def config_dev_info(self):
        logger.debug('Requesting config branch info: {}/{}'.format(CONFIG_REPO, CONFIG_BRANCH))
        return self.github.get_branch_info(CONFIG_REPO, CONFIG_BRANCH)['head']

    @cached_property
    def app_merged_info(self):
        app_merged_branch_name = 'sparrow-test-{}-{}'.format(self.app_branch_info[SHA], self.app_dev_info[SHA])

        logger.debug('Requesting app branch info: {}/{}'.format(self.repo_name, app_merged_branch_name))
        try:
            app_merged_info = self.github.get_branch_info(self.repo_name, app_merged_branch_name)['head']
            # branch already exists, could check if it is complete but assume that for now
            # todo: maybe add double-check
            return app_merged_info
        except GithubException as e:
            if e.status == 404 and e.data.get('message') == 'Branch not found':
                logger.debug('Branch does not exist, will attempt to create it...')
            else:
                raise

        app_merged_info = self.github.create_merged_ref(self.repo_name, app_merged_branch_name, self.app_branch_info[SHA],
                                                        APP_TARGET_BRANCH)

        return app_merged_info['head']

    @cached_property
    def branch_test_run(self):
        return self.find_or_create_test_run(COMPARE_URL,
                                            self.app_branch_info[REF],
                                            self.app_merged_info[SHA],
                                            self.config_dev_info[SHA])

    @cached_property
    def dev_test_run(self):
        return self.find_or_create_test_run(COMPARE_URL,
                                            self.app_dev_info[REF],
                                            self.app_dev_info[SHA],
                                            self.config_dev_info[SHA])
