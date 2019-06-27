


# Development

- `docker-compose build` - build everything needed for local development.
- `docker-compose up web` - start Django development container. It should automatically reload when code change.
- `bin/test.sh` - run all tests in Django development container.
- `bin/coverage.sh` - run all tests and print code coverage in Django development container.
- `bin/manage.sh` - run any and all of your Django command in production, beta, staging or local environment. See `bin/manage.sh -h` for detail usage.
- **important:** If you ever need to SSH into container, look it up yourself. It should not be necessary in 99% of cases. And if you ever need to SSH in then you should really know what you're doing so no guidance is provided.
- `bin/build_apiary.sh` - update apiary.apib file. Please run this when ever you change any apiary file. **Note**: please install [hercule](https://github.com/jamesramsay/hercule) first.

# Gain access to kubernetes cluster

- `brew install gettext`
- [install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [install gcloud](https://cloud.google.com/sdk/docs/downloads-interactive)
- `gcloud auth login`
- `gcloud container clusters get-credentials cpdp-gke --zone us-central1-a --project twitterbot-180604`

# Setup production/beta/staging

1. `git secret reveal`
2. `bin/initialize_kubernetes_cluster.sh` - again only run this when cluster is newly created.

# Run Django command on staging, beta or production

Use `bin/run_job.sh` e.g. `bin/run_job.sh --staging latest cache_data`. Check `bin/run_job.sh -h` for usage.

# Setup cronjob on staging, beta or production

Run `bin/run_cronjob.sh` to run individual cronjobs e.g. `bin/run_cronjob.sh --staging update_documents @daily latest`. Check `bin/run_cronjob.sh -h` for usage.

# Deployment

Deployment should be almost automatic depending on which branch you pushed. `master` branch push will trigger production deploy whereas `staging` branch push will trigger staging deploy. Staging deployment is completely automated but production deployment require your approval (to proceed) between `django_migrate` step and `rebuild_index` step so that you have the chance to run a command that alter data such as `cache_data`. If you want to see each step, look at `.circleci/config.yml`.

Content of `kubernetes` folder:
- `cpdpbot.yml` - cpdpbot (Twitter bot) deployment.
- `elasticsearch.yml` - Elasticsearch deployment and service.
- `gunicorn.yml` - Gunicorn deployment and service.
- `ingress.yml` - Main ingress.
- `namespaces.yml` - All namespaces.
- `pg_proxy.yml` - Postgres CloudSQL Proxy
- `redis.yml` - Redis deployment and service.
- `secrets-production.yml` - Secrets for production
- `secrets-beta.yml` - Secrets for beta
- `secrets-staging.yml` - Secrets for staging
- `job` - manifest file for job.
- `cronjob` - manifest file for cronjob.

Most of our resources are deployed into 3 namespaces: `staging`, `beta` and `production` therefore most commands should specify either of these 2 namespaces e.g.
- `kubectl get pods -n staging` - look up all pods in namespace staging
- `kubectl get services -n staging` - look up all services in namespace staging
- `kubectl logs update-documents-69567775bc-hr86t -n staging` - look at logs from pod `update-documents-69567775bc-hr86t`

# Make changes to Docker images

The following Docker images rarely change so you have to update and build/push them manually when there is a change. Run the following snippets depending on which docker image you changed:

- `docker build -t cpdbdev/postgres:9.6 docker/postgres && docker push cpdbdev/postgres:9.6`
- `docker build -t cpdbdev/remote_syslog2:latest docker/remote_syslog2 && docker push cpdbdev/remote_syslog2:latest`

# Add kubernetes secrets

Secrets for staging, beta and production are stored in following files `kubernetes/secrets-staging.yml.secret`, `kubernetes/secrets-beta.yml.secret` and `kubernetes/secrets-production.yml.secret`
Run `git secret reveal` to show the secret manifest file.

Secret values are all base64 encoded by running `echo -n <value> | base64`
To reveal the secret value `echo <base64 encoded string> | base64 -D`

# Twitter bot

Twitter bot (@CPDPbot) is made of 2 parts: webhook run in Django and cpdpbot worker. Below is guidance for webhook. To know how to change cpdpbot worker, look at `docker/cpdpbot/DEVELOPMENT.md`.

## Development
Please make sure you have correct development tokens on local environment (.env file)
- Install `ngrok` to expose webhook to twitter.
- Run backend server
- `ngrok http 8000`.
- Run command `manage.py register_webhook --url=<ngrok_url>/api/v2/twitter/webhook/` to register webhook.
- Run command `manage.py add_account_subscription` and follow the instruction to subscribe twitter account.

## Deployment
This only needs to be done once unless the webhook url or subscrition was changed.
- Run command `manage.py register_webhook --url=https://cpdp.co/api/v2/twitter/webhook/` to register webhook.
- Run command `manage.py add_account_subscription`.
- Go to the provided authenticaton url and login using CPDPBot account (get from 1Password) to get PIN number.
- Input PIN number to continue.

Some other available commands:
- `remove_webhook --id=<webhook_id>` to remove a webhook and all subscriptions.
- `list_webhooks` to list added webhooks.
- `list_subscriptions` to list all subscription accounts.
- `add_owner_subscription` quick command to subscribe the owner of the twitter app.
- `remove_subscription` to remove subscription account.

# AWS Lambda
We use S3 and Lambda from AWS. We store all xlsx files, pdf attachment files on S3 and built officer zip files on S3. We use Lambda to upload pdf files and create zip files on the fly.
- All credentials are available in the encoded env files

## Development
All Lambda source is at `lambda` directory. Each Lambda function is at a subdirectory, e.g. `lambda/create_officer_zip`.
A Lambda function package should at least contain these files:
- `.env` which contains `FUNCTION_NAME` variable
- `lambda_function.py` which defined `lambda_handler` function
- `requirements.txt` for installing packages via **pip**
- All other packages and modules which is used by the `lambda_handler` function.

**Note**: Dont use `package` to name your packages, because we will install all 3rd party packages into `package`

- Run tests with `docker-compose run web python -m lambda.test`

## Deploy lambda function
- Dev must create Lambda functions manually on AWS console
- To deploy/update Lambda functions, use `docker-compose run web lambda/deploy.sh`

# Setup SSL Certificates

- [Detail](docs/setup-ssl-certificates.md)

# Troubleshooting

- [Adding CA public key to google-cloud-sdk image for API healthcheck](docs/api-healthcheck.md)

# Miscelaneous

- [API standards](docs/api-standards.md)
