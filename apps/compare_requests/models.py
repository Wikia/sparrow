# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from common.github_integration import GitHub

from test_runs.models import test_run_status_changed, TestRunStatus, TestRun


class CompareRequest(models.Model):
    id = models.AutoField(primary_key=True)

    repo = models.CharField(max_length=100)
    pull_request_num = models.IntegerField()

    base_ref = models.CharField(max_length=250)
    base_sha = models.CharField(max_length=40)
    base_test_run = models.ForeignKey('test_runs.TestRun', related_name='base_in_compare_requests')

    head_ref = models.CharField(max_length=250)
    head_sha = models.CharField(max_length=40)
    head_test_run = models.ForeignKey('test_runs.TestRun', related_name='head_in_compare_requests')

    created = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __unicode__ = __repr__

    __str__ = __repr__

    def assess_comparison(self):
        """
        Given the fact test runs have been completed, generate the comparison
        and post the results back to github
        """
        base_test_run = self.base_test_run
        head_test_run = self.head_test_run

        if base_test_run.status == TestRunStatus.ERROR or head_test_run.status == TestRunStatus.ERROR:
            self.notify_error()
            return

        comparison_text = self.build_comparison_text()
        self.notify_pull_request(comparison_text)

    def build_comparison_text(self):
        """
        Generate comparison text
        """
        comparison_text = "Performance comparison results placeholder.\nTests executed: {} and {}".format(
            self.base_test_run_id, self.head_test_run_id
        )
        return comparison_text

    def notify_error(self):
        """
        Add comment about test execution error
        """

        text = "Performance comparison ended up with errors. Please inspect logs for more details."
        self.notify_pull_request(text)

    def notify_pull_request(self, text):
        """
        Add comment in associated pull request

        :param text: Comment body
        :return:
        """
        github = GitHub()
        github.post_pull_request_comment(self.repo,self.pull_request_num,text)

@receiver(test_run_status_changed, sender=TestRun)
def test_run_changed(sender, instance, **kwargs):
    """ Callback which synchronises TestRun status with Tasks statuses.

    Here lies simple logic which tries to synch TestRun status with all sub-Tasks
    statuses. It covers some very basic cases such as:
        * starting Task starts parent TestRun
        * any error in Task will result in setting error on parent TestRun
        * finishing all sub-Task will mark TestRun as done

    :param instance:
    :type instance: TestRun
    """
    if instance.status not in (TestRunStatus.DONE, TestRunStatus.ERROR):
        return

    test_run_id = instance.id
    compare_requests = CompareRequest.objects.filter(
        Q(base_test_run_id=test_run_id) | Q(head_test_run_id=test_run_id)
    )

    for compare_request in compare_requests:
        if compare_request.base_test_run.completed and compare_request.head_test_run.completed:
            compare_request.assess_comparison()
