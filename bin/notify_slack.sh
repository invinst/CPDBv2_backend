#!/usr/bin/env sh

REPOSITORY="CPDBv2_backend"
DEV_SHA="$(git --no-pager show HEAD^2 --pretty=%h)"
PR_FILE="deploy_prs_$(echo $REPOSITORY)_$DEV_SHA.csv"
STORIES_FILE="deploy_stories_$(echo $REPOSITORY)_$DEV_SHA.csv"
wget http://storage.googleapis.com/cpdp-deploy-artifacts/$PR_FILE
wget http://storage.googleapis.com/cpdp-deploy-artifacts/$STORIES_FILE

deploy_prs="$(cat $PR_FILE | sed -En 's/([^,]+),(.+).$/{"color": "#36a64f"\, "title": "\2", "title_link": "\1"}/p' | paste -s -d"," -)"
deploy_stories="$(cat $STORIES_FILE | sed -En 's/([^,]+),(.+).$/{"color": "#028090"\, "title": "\2", "title_link": "\1"}/p' | paste -s -d"," -)"

wget --header 'Content-type: application/json' \
    --post-data "{\"text\": \"Finished deploy for repo $REPOSITORY.\",\"attachments\": [{\"title\":\"Deployed pull requests:\"},$deploy_prs,{\"title\":\"Deployed PT stories:\"},$deploy_stories] }" \
    $CPDP_DEPLOY_NOTIFIER_WEBHOOK
