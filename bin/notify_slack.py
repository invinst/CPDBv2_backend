#!/usr/bin/env python

import requests
import os
import csv
import json
from subprocess import check_output


REPOSITORY = "CPDBv2_backend"
dir_path = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.join(dir_path, '..')


def call_cmd(cmd):
    return check_output(
        cmd, shell=True, cwd=root_dir
    ).strip()


def download_file(file):
    output_path = os.path.join(root_dir, file)
    call_cmd(
        'wget http://storage.googleapis.com/cpdp-deploy-artifacts/%s -O %s' % (file, output_path)
    )

    return output_path


def file_to_message_json(file_path, title, color):
    messages = [{
        'title': title
    }]

    with open(file_path, encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            messages.append({
                'color': color,
                'title': row[1],
                'title_link': row[0]
            })
    return messages


if __name__ == "__main__":
    DEV_SHA = call_cmd("git --no-pager show HEAD^2 --pretty=%h")
    PR_FILE = "deploy_prs_%s_%s.csv" % (REPOSITORY, DEV_SHA)
    STORIES_FILE = "deploy_stories_%s_%s.csv" % (REPOSITORY, DEV_SHA)

    pr_file_path = download_file(PR_FILE)
    stories_file_path = download_file(STORIES_FILE)

    attachments = file_to_message_json(pr_file_path, 'Deployed pull requests:', '#36a64f') + \
        file_to_message_json(stories_file_path, 'Deployed PT stories:', '#028090')

    requests.post(
        os.environ['CPDP_DEPLOY_NOTIFIER_WEBHOOK'],
        headers={'Content-type': 'application/json'},
        data=json.dumps({
            'text': 'Finished deploy for repo %s.' % REPOSITORY,
            'attachments': attachments
        }))
