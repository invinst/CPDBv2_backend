# Kubernetes

## Gain access to kubernetes cluster

- `brew install gettext`
- [install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [install gcloud](https://cloud.google.com/sdk/docs/downloads-interactive)
- `gcloud auth login`
- `gcloud container clusters get-credentials cpdp-gke --zone us-central1-a --project twitterbot-180604`

## Config files
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

## Namespaces
Most of our resources are deployed into 3 namespaces: `staging`, `beta` and `production` therefore most commands should specify either of these 3 namespaces e.g.
- `kubectl get pods -n staging` - look up all pods in namespace staging
- `kubectl get services -n staging` - look up all services in namespace staging
- `kubectl logs update-documents-69567775bc-hr86t -n staging` - look at logs from pod `update-documents-69567775bc-hr86t`

## Make changes to Docker images

The following Docker images rarely change so you have to update and build/push them manually when there is a change. Run the following snippets depending on which docker image you changed:

- `docker build -t cpdbdev/postgres:9.6 docker/postgres && docker push cpdbdev/postgres:9.6`
- `docker build -t cpdbdev/remote_syslog2:latest docker/remote_syslog2 && docker push cpdbdev/remote_syslog2:latest`

## Add kubernetes secrets

Secrets for staging, beta and production are stored in following files `kubernetes/secrets-staging.yml.secret`, `kubernetes/secrets-beta.yml.secret` and `kubernetes/secrets-production.yml.secret`
Run `git secret reveal` to show the secret manifest file.

Secret values are all base64 encoded by running `echo -n <value> | base64`
To reveal the secret value `echo <base64 encoded string> | base64 -D`
