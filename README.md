


# Development

- `docker-compose build` - build everything needed for local development.
- `docker-compose up web` - start Django development container. It should automatically reload when code change.
- `bin/test.sh` - run all tests in Django development container.
- `bin/coverage.sh` - run all tests and print code coverage in Django development container.
- `bin/manage.sh` - run any and all of your Django command in Django development container.
- **important:** If you ever need to SSH into container, look it up yourself. It should not be necessary in 99% of cases. And if you ever need to SSH in then you should really know what you're doing so no guidance is provided.

# Setup production/staging

1. `git secret reveal`
2. `az aks get-credentials --output json --resource-group terraformed --name cpdp-aks-cluster` - get kubectl credentials.
2. `terraform apply --target azurerm_kubernetes_cluster.cpdp_aks_cluster terraform` - create or change Azure AKS config which back our kubernetes cluster. Note that you should not run this unless there is a change in terraform config.
3. `bin/initialize_kubernetes_cluster.sh` - again only run this when cluster is newly created.
4. `bin/setup_cronjobs.sh` - setup cronjobs either for staging or production. For now only setup cronjob for production.

# Deployment

Deployment should be almost automatic depending on which branch you pushed. `master` branch push will trigger production deploy whereas `staging` branch push will trigger staging deploy. Staging deployment is completely automated but production deployment require your approval (to proceed) between `django_migrate` step and `rebuild_index` step so that you have the chance to run a command that alter data such as `cache_data`. If you want to see each step, look at `.circleci/config.yml`.

If you need to run any command on production/staging, use `bin/run_job.sh` e.g. `bin/run_job.sh --staging cache_data.yml latest`

Content of `kubernetes` folder:
- `cpdpbot.yml` - cpdpbot (Twitter bot) deployment.
- `elasticsearch.yml` - Elasticsearch deployment and service.
- `gunicorn.yml` - Gunicorn deployment and service.
- `ingress.yml` - Main ingress.
- `namespaces.yml` - All namespaces.
- `postgres.yml` - Postgres deployment and service.
- `redis.yml` - Redis deployment and service.
- `secrets.yml` - Secrets
- `jobs` - manifest files of all jobs.
- `cronjobs` - manifest files of all cronjobs.

Most of our resources are deployed into 2 namespaces: `staging` and `production` therefore most commands should specify either of these 2 namespaces e.g.
- `kubectl get pods -n staging` - look up all pods in namespace staging
- `kubectl get services -n staging` - look up all services in namespace staging
- `kubectl logs update-documents-69567775bc-hr86t -n staging` - look at logs from pod `update-documents-69567775bc-hr86t`

# Make changes to Docker images

The following Docker images rarely change so you have to update and build/push them manually when there is a change. Run the following snippets depending on which docker image you changed:

- `docker build -t cpdbdev/kubectl:latest docker/kubectl && docker push cpdbdev/kubectl:latest`
- `docker build -t cpdbdev/postgres:9.6 docker/postgres && docker push cpdbdev/postgres:9.6`
- `docker build -t cpdbdev/remote_syslog2:latest docker/remote_syslog2 && docker push cpdbdev/remote_syslog2:latest`

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

# Miscelaneous

- [API standards](docs/api-standards.md)
- [Backup Elasticsearch via snapshot](docs/backup-elasticsearch-snapshot.md)

