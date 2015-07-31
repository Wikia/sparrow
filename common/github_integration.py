from django.conf import settings

import github


class MergeFailed(Exception):
    pass

class GitHub(object):
    def __init__(self):
        self.github = github.Github(settings.GITHUB_TOKEN)
        self.repo_cache = {}

    def get_repo(self, repo_name):
        if not repo_name in self.repo_cache:
            self.repo_cache[repo_name] = self.github.get_repo(repo_name)
        return self.repo_cache[repo_name]

    def get_branch_info(self, repo_name, branch_name):
        repo = self.get_repo(repo_name)
        branch = repo.get_branch(branch_name)
        return {
            'repo': repo_name,
            'head': {
                'ref': branch_name,
                'sha': branch.commit.sha,
            }
        }

    def get_pull_request_info(self, repo_name, pull_num):
        pull_req = self.get_repo(repo_name).get_pull(pull_num)
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
        pull_req = self.get_repo(repo_name).get_pull(pull_num)
        pull_req.create_issue_comment(comment_body)

    def create_merged_ref(self, repo_name, target_ref_name, *shas):
        target_ref_full_name = 'refs/heads/{}'.format(target_ref_name)
        repo = self.get_repo(repo_name)
        target_ref = repo.create_git_ref(target_ref_full_name, shas[0])

        try:
            for i in range(1, len(shas)):
                merge_commit = repo.merge(target_ref.ref, shas[i], 'Sparrow Code Setup: Merging "{}"'.format(shas[i]))
        except github.GithubExceptionion as e:
            raise MergeFailed('Git merge failed', e)

        return {
            'repo': repo_name,
            'head': {
                'ref': target_ref.ref,
                'sha': merge_commit.sha
            }
        }

