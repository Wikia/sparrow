from django.conf import settings

import github


class GitHub(object):
    def __init__(self):
        self.github = github.Github(settings.GITHUB_TOKEN)

    def get_branch_info(self, repo_name, branch_name):
        repo = self.github.get_repo(repo_name)
        branch = repo.get_branch(branch_name)
        return {
            'repo': repo_name,
            'head': {
                'ref': branch_name,
                'sha': branch.commit.sha,
            }
        }

    def get_pull_request_info(self, repo_name, pull_num):
        pull_req = self.github.get_repo(repo_name).get_pull(pull_num)
        return {
            'repo': repo_name,
            'pull_num': pull_num,
            'base': {
                'ref': pull_req.base.ref,
                'sha': pull_req.base.sha,
            },
            'head': {
                'ref': pull_req.head.ref,
                'sha': pull_req.head.sha,
            }
        }

    def post_pull_request_comment(self, repo_name, pull_num, comment_body):
        pull_req = self.github.get_repo(repo_name).get_pull(pull_num)
        pull_req.create_issue_comment(comment_body)
