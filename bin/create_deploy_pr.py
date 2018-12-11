#!/usr/bin/env python

from subprocess import check_output
import os
import json
import urllib2
import csv
import cStringIO
import codecs
import sys
from datetime import datetime

import requests

PROJECT_ID = 1340138
REPO = 'CPDBv2_backend'

dir_path = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.join(dir_path, '..')


class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, encoding='utf-8', **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode('utf-8') for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def call_cmd(cmd):
    return check_output(
        cmd, shell=True, cwd=root_dir
    ).strip()


def get_latest_code():
    call_cmd('git checkout develop')
    call_cmd('git pull')
    call_cmd('git checkout master')
    call_cmd('git pull')


def get_deploy_prs_and_stories():
    current_branch = call_cmd("git branch | grep \\* | cut -d ' ' -f2")
    call_cmd('git checkout master')
    cur_id = call_cmd("git rev-parse HEAD")
    call_cmd(f'git checkout -b master-{cur_id}')
    call_cmd('git merge develop -q -m "Merge changes from develop"')
    prs = call_cmd(
        f"git --no-pager log {cur_id}..HEAD --pretty=oneline --abbrev-commit --grep 'Merge pull request' | "
        "sed -E 's/.+Merge pull request #([0-9]+).+/\\1/p' | sort -u -"
    )
    stories = call_cmd(
        f"git --no-pager log {cur_id}..HEAD --abbrev-commit | grep -E 'pivotaltracker' | "
        "sed -E 's/.+pivotaltracker.com\\/story\\/show\\/([0-9]+).*/\\1/p' | sort -u -"
    )
    call_cmd(f'git checkout {current_branch}')
    call_cmd(f'git branch -D master-{cur_id}')
    return filter(None, prs.split('\n')), filter(None, stories.split('\n'))


def get_auth_token(name, file_path, prompt):
    try:
        token_file = open(file_path)
        return token_file.read()
    except IOError:
        print(f'{name} token is not found.')
        token = raw_input(prompt)
        with open(file_path, 'w') as token_file:
            token_file.write(token)
        print(f'Token saved to file {file_path}')
        return token


def check_story_statuses(stories):
    unaccepted_stories = [s for s in stories if s['current_state'] != 'accepted']
    if len(unaccepted_stories) > 0:
        print('The following stories have not been accepted yet:')
        for s in unaccepted_stories:
            print(f"{s['name']} - {s['url']}")
        confirm = raw_input('Do you want to continue? [Y/n]')
        if confirm.lower() == 'n':
            sys.exit(0)


def get_pt_stories(story_ids):
    if len(story_ids) == 0:
        return []

    pt_token = get_auth_token(
        'Pivotaltracker',
        os.path.expanduser('~/.pivotaltrackertoken'),
        'Enter Pivotaltracker token: '
    )
    req = urllib2.Request(
        f"https://www.pivotaltracker.com/services/v5/projects/{PROJECT_ID}/stories?filter=id:{','.join(story_ids)}"
    )
    req.add_header('X-TrackerToken', pt_token)
    response = urllib2.urlopen(req)
    stories = json.loads(response.read())
    check_story_statuses(stories)

    return stories


def see_any_header(body, i):
    return i < len(body) - 2 and body[i + 1].startswith('--')


def build_pr_body(pr_ids, pt_stories, pr_deploy_notes):
    result = []
    result += ['Pull requests', '--', '']

    for pr_id in pr_ids:
        result.append(f'- #{pr_id}')

    if len(pt_stories) > 0:
        result += ['', 'Pivotal tracker stories', '--', '']
        for story in pt_stories:
            result.append(f"- [{story['name']}]({story['url']})")

    if len(pr_deploy_notes) > 0:
        result += ['', 'Deploy Notes', '--', '']
        for pr_id, deploy_note in pr_deploy_notes:
            result.append(f'- #{pr_id}')
            for note in deploy_note:
                result.append(f'  {note}')

    return '\r\n'.join(result)


def get_pr_deploy_notes(pr_ids, github_token):
    pr_deploy_notes = []
    prs = []

    for pr_id in pr_ids:
        req = urllib2.Request(f'https://api.github.com/repos/EastAgile/{REPO}/pulls/{pr_id}')
        req.add_header('Authorization', f'token {github_token}')
        response = urllib2.urlopen(req)
        pr = json.loads(response.read())
        prs.append(pr)
        body = pr['body'].split('\r\n')
        i = 0
        deploy_section = False
        deploy_notes = []

        while i < len(body):
            line = body[i]
            if see_any_header(body, i):
                if body[i].lower().startswith('deploy note'):
                    i += 2
                    deploy_section = True
                    continue
                elif deploy_section:
                    break
            elif deploy_section:
                deploy_notes.append(line)
            i += 1
        if len(deploy_notes) > 0:
            pr_deploy_notes.append((pr_id, [note for note in deploy_notes if note]))

    return pr_deploy_notes, prs


def create_deployment_pr(pr_body, github_token):
    pr_data = {
        'title': f'Production deploy {datetime.now()}',
        'body': pr_body,
        'head': 'develop',
        'base': 'master'
    }

    data = json.dumps(pr_data)
    headers = {
        'Authorization': f'token {github_token}'
    }

    response = requests.post(
        url=f'https://api.github.com/repos/EastAgile/{REPO}/pulls',
        headers=headers,
        data=data
    )

    response.raise_for_status()

    result = response.json()

    print('PR has been created successfully!')
    print(result['html_url'])


if __name__ == "__main__":
    get_latest_code()

    pr_ids, story_ids = get_deploy_prs_and_stories()
    if len(pr_ids) == 0:
        print('No difference between master and develop.')
        sys.exit(0)

    pt_stories = get_pt_stories(story_ids)

    github_token = get_auth_token(
        'Github',
        os.path.expanduser('~/.githubtoken'),
        'Enter Gihub API token (with repos permission): '
    )

    pr_deploy_notes, prs = get_pr_deploy_notes(pr_ids, github_token)
    deployment_pr_body = build_pr_body(pr_ids, pt_stories, pr_deploy_notes)

    create_deployment_pr(deployment_pr_body, github_token)
