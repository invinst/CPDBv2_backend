# CPDP API

## Table of contents
* [Development](#development)
* [Deployment](#deployment)
* [API Docs](#api-docs)
* [Development guides](#development-guides)

## Development

### Getting Started

- `docker-compose build` - build everything needed for local development.
- `docker-compose up web` - start Django development container. It should automatically reload when code change.
- `bin/manage.sh` - run any and all of your Django command in production, beta, staging or local environment. See `bin/manage.sh -h` for detail usage.

### Tests

- `bin/test.sh` - run all tests in Django development container.
- `bin/coverage.sh` - run all tests and print code coverage in Django development container.

### CircleCi 

Environment Variables

- `SKIP_COVERALLS`: set to `true` to skip sending coverage report to Coveralls. Only do this if Coveralls is down.
- `$SKIP_REBUILD_INDEX`: set to `true` to skip rebuild index. This will significantly reduce deployment time. Please make sure that no changes in database was made.
- `$SKIP_REBUILD_SEARCH_INDEX`: set to `true` to skip rebuild search index. This will significantly reduce deployment time. Please make sure that no changes in database was made.

## Deployment

Deployment should be almost automatic depending on which branch you pushed. 
- `master` branch push will trigger production deploy
- `beta` branch push will trigger beta deploy
- `staging` branch push will trigger staging deploy

Staging deployment is completely automated but production deployment require your approval (to proceed) between `django_migrate` step and `rebuild_index` step so that you have the chance to run a command that alter data such as `cache_data`. 

If you want to see each step, look at `.circleci/config.yml`.

### Kubernetes 

- Read [Kubernetes guides](docs/kubernetes.md)

### Setup production/beta/staging

1. `git secret reveal`
2. `bin/initialize_kubernetes_cluster.sh` - again only run this when cluster is newly created.
3. `bin/initialize_kubernetes_namespace.sh`.

### Setup cronjob on staging, beta or production

- Run `bin/run_cronjob.sh` to run individual cronjobs e.g. `bin/run_cronjob.sh --staging update_documents 0 5 * * * latest`. Check `bin/run_cronjob.sh -h` for usage.
- Kubernetes uses UTC so we have to +5 to match with Chicago time zone.
- **Do not** use @daily as it will makes the cronjobs run at 19:00 CDT.

### Run Django command on staging, beta or production

- Use `bin/run_job.sh` e.g. `bin/run_job.sh --staging latest cache_data`. Check `bin/run_job.sh -h` for usage.

## API Docs

- Install [hercule](https://github.com/jamesramsay/hercule)
- Run `bin/build_apiary.sh` to update apiary file.


## Development guides

- [API standards](docs/api-standards.md)
- [Setup SSL Certificates](docs/setup-ssl-certificates.md)
- [Twitter bot](docs/twitter-bot.md)
- [AWS Lambda](docs/aws-lambda.md)
