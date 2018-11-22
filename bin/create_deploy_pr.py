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
gs_bucket = 'cpdp-deploy-artifacts'

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
    call_cmd('git checkout -b master-%s' % cur_id)
    call_cmd('git merge develop -q -m "Merge changes from develop"')
    prs = call_cmd(
        "git --no-pager log %s..HEAD --pretty=oneline --abbrev-commit --grep 'Merge pull request' | "
        "sed -E 's/.+Merge pull request #([0-9]+).+/\\1/p' | sort -u -" % cur_id
    )
    stories = call_cmd(
        "git --no-pager log %s..HEAD --abbrev-commit | grep -E 'pivotaltracker' | "
        "sed -E 's/.+pivotaltracker.com\\/story\\/show\\/([0-9]+).*/\\1/p' | sort -u -" % cur_id
    )
    call_cmd('git checkout %s' % current_branch)
    call_cmd('git branch -D master-%s' % cur_id)
    return filter(None, prs.split('\n')), filter(None, stories.split('\n'))


def get_auth_token(name, file_path, prompt):
    try:
        token_file = open(file_path)
        return token_file.read()
    except IOError:
        print('%s token is not found.' % name)
        token = raw_input(prompt)
        with open(file_path, 'w') as token_file:
            token_file.write(token)
        print('Token saved to file %s' % file_path)
        return token


def check_story_statuses(stories):
    unaccepted_stories = [s for s in stories if s['current_state'] != 'accepted']
    if len(unaccepted_stories) > 0:
        print('The following stories have not been accepted yet:')
        for s in unaccepted_stories:
            print('%s - %s' % (s['name'], s['url']))
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
        'https://www.pivotaltracker.com/services/v5/projects/%s/stories?filter=id:%s' %
        (PROJECT_ID, ','.join(story_ids))
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
        result.append('- #%s' % pr_id)

    if len(pt_stories) > 0:
        result += ['', 'Pivotal tracker stories', '--', '']
        for story in pt_stories:
            result.append('- [%s](%s)' % (story['name'], story['url']))

    if len(pr_deploy_notes) > 0:
        result += ['', 'Deploy Notes', '--', '']
        for pr_id, deploy_note in pr_deploy_notes:
            result.append('- #%s' % pr_id)
            for note in deploy_note:
                result.append('  %s' % note)

    return '\r\n'.join(result)


def get_pr_deploy_notes(pr_ids, github_token):
    pr_deploy_notes = []
    prs = []

    for pr_id in pr_ids:
        req = urllib2.Request('https://api.github.com/repos/EastAgile/%s/pulls/%s' % (REPO, pr_id))
        req.add_header('Authorization', 'token %s' % github_token)
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
        'title': 'Production deploy %s' % datetime.now(),
        'body': pr_body,
        'head': 'develop',
        'base': 'master'
    }

    data = json.dumps(pr_data)
    headers = {
        'Authorization': 'token %s' % github_token
    }

    response = requests.post(
        url='https://api.github.com/repos/EastAgile/%s/pulls' % REPO,
        headers=headers,
        data=data
    )

    response.raise_for_status()

    result = response.json()

    print('PR has been created successfully!')
    print(result['html_url'])


def get_develop_hash():
    call_cmd('git checkout develop')
    return call_cmd('git --no-pager show HEAD --pretty=%h').strip()


def upload_deploy_prs(prs, dev_hash):
    file_path = os.path.join(root_dir, 'deploy_prs_%s_%s.csv' % (REPO, dev_hash))
    with open(file_path, 'w') as f:
        csv_writer = UnicodeWriter(f)
        for pr in prs:
            csv_writer.writerow([pr['html_url'], pr['title']])
    call_cmd('gsutil cp %s gs://%s/' % (file_path, gs_bucket))
    call_cmd('rm %s' % file_path)


def upload_deploy_stories(stories, dev_hash):
    file_path = os.path.join(root_dir, 'deploy_stories_%s_%s.csv' % (REPO, dev_hash))
    with open(file_path, 'w') as f:
        csv_writer = UnicodeWriter(f)
        for story in stories:
            csv_writer.writerow([story['url'], story['name']])
    call_cmd('gsutil cp %s gs://%s/' % (file_path, gs_bucket))
    call_cmd('rm %s' % file_path)


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

    dev_hash = get_develop_hash()

    upload_deploy_prs(prs, dev_hash)
    upload_deploy_stories(pt_stories, dev_hash)

    create_deployment_pr(deployment_pr_body, github_token)
