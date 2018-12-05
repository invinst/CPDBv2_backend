#!/usr/bin/env python

import os
import re
import sys
import json
import argparse
from subprocess import check_output

import requests


repository = "CPDBv2_backend"
project_id = '1340138'
github_token = os.environ['GITHUB_REPO_TOKEN']
pt_token = os.environ['PIVOTAL_TRACKER_TOKEN']
dir_path = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.join(dir_path, '..')
ptid_pattern = re.compile(r'\[\#(\d+)\]')


def call_cmd(cmd):
    return check_output(
        cmd, shell=True, cwd=root_dir
    ).decode('utf-8').strip()


def get_pr(pr_num):
    pr_endpoint = 'https://api.github.com/repos/EastAgile/%s/pulls/%s' % (repository, pr_num)
    return requests.get(pr_endpoint, headers={'Authorization': 'token %s' % github_token}).json()


def get_commits(pr):
    return requests.get(pr['commits_url'], headers={'Authorization': 'token %s' % github_token}).json()


def extract_ptid_from_commit_message(msg):
    match = re.search(ptid_pattern, msg)
    if match is not None:
        return match.group(1)
    return None


def get_stories(pr):
    commits = get_commits(pr)
    ptids = list(filter(None, [
        extract_ptid_from_commit_message(commit['commit']['message'])
        for commit in commits
    ]))
    if len(ptids) == 0:
        return []
    ptids = list(set(ptids))
    return requests.get(
        'https://www.pivotaltracker.com/services/v5/projects/%s/stories?filter=id:%s' %
        (project_id, ','.join(ptids)),
        headers={'X-TrackerToken': pt_token}
    ).json()


def get_pr_nums(pr):
    lines = pr['body'].split('\r\n')
    i = 0
    pr_section = False
    pr_lines = []

    while i < len(lines):
        line = lines[i]
        if i < len(lines) - 2 and lines[i + 1].startswith('--'):
            if lines[i].lower().startswith('pull requests'):
                i += 2
                pr_section = True
                continue
            elif pr_section:
                break
        elif pr_section:
            pr_lines.append(line)
        i += 1
    return [
        re.sub(r'- #(\d+)', r'\1', val)
        for val in pr_lines
        if val != ''
    ]


def pr_attachment(pr):
    return {
        'color': '#36a64f',
        'title': pr['title'],
        'title_link': pr['html_url']
    }


def pt_attachment(pt_story):
    return {
        'color': '#028090',
        'title': pt_story['name'],
        'title_link': pt_story['url']
    }


def section_attachment(title):
    return {
        'title': title
    }


def notify_slack(prs=None, stories=None):
    attachments = []
    if prs is not None and len(prs):
        attachments.append(section_attachment('Deployed pull requests:'))
        attachments += [
            pr_attachment(pr)
            for pr in prs
        ]
    if stories is not None and len(stories):
        attachments.append(section_attachment('Deployed PT stories:'))
        attachments += [
            pt_attachment(story)
            for story in stories
        ]
    requests.post(
        os.environ['CPDP_DEPLOY_NOTIFIER_WEBHOOK'],
        headers={'Content-type': 'application/json'},
        data=json.dumps({
            'text': 'Finished deploy for repo %s.' % repository,
            'attachments': attachments
        }))


if __name__ == "__main__":
    default_pr_num = call_cmd(
        r"git --no-pager show HEAD --pretty=%B | sed -En 's/Merge pull request \#([0-9]+).+/\1/p'"
    )
    parser = argparse.ArgumentParser(description='Notify Slack of deployment success!')
    parser.add_argument(
        'pr_num', nargs='?',
        default=default_pr_num,
        help=(
            'pull request number to operate upon. If this is not specified '
            'then it will be extracted from last commit message.'
        )
    )
    args = parser.parse_args()
    parent_pr_num = args.pr_num
    if not parent_pr_num:
        print("Not a pull request. Don't commit to master branch directly!")
        sys.exit(0)

    pr = get_pr(parent_pr_num)

    if pr['head']['ref'].startswith('hotfix'):
        child_prs = [pr]
        child_stories = get_stories(pr)
        notify_slack(prs=child_prs, stories=child_stories)

    elif pr['head']['ref'] == 'develop':
        pr_nums = get_pr_nums(pr)
        child_prs = [
            get_pr(pr_num)
            for pr_num in pr_nums
        ]
        child_stories = get_stories(pr)
        notify_slack(prs=child_prs, stories=child_stories)

    else:
        print("Pull request head is neither hotfix nor develop (%s). Don't know what to do." % pr['head']['ref'])
        sys.exit(0)
