


# Development

Please make sure that you have `vagrant 1.8.6` and `ansible 2.1.3.0` on your machine, we use them as isolated development environment and automation tools.

You'll then need to manually create these files - ask the team to give them to you:

- `../vault_pass.txt` (parent dir of this repo): This file is used to decrypt ansible variables contained in `ansible/env_vars/secrets.yml` and `ansible/env_vars/vagrant-secrets.yml` files.
- `./initial_dump.sql`: Initial Db dump. Running `vagrant provision` should pick this up and delete it automatically after importing.


Ansible variables in `ansible/env_vars/secrets.yml` and `ansible/env_vars/vagrant-secrets.yml` files:
- `ssl_key_password`: password for ssl key
- `ssl_crt`: ssl certificate
- `ssl_key`: ssl key
- `db_user`: Database user name
- `db_name`: Database name
- `db_password`: Database password
- `django_settings_module`: Django settings module
- `django_debug`: Debug mode
- `database_url`: Database url
- `django_secret_key`: Django secret key
- `mailchimp_api_key`: Mailchimp api key
- `mailchimp_user`: Mailchimp user name
- `azure_storage_account_name`: Azure storage account name
- `azure_storage_account_key`: Azure store account key
- `mailgun_api_key`: Mailgun api key
- `newrelic_license`: Newrelic license key

Then just `vagrant up --provision` and wait for ansible to do its things. When the provision is done, you may find your application running at ip `192.168.50.100` (you can change them in `Vagrantfile`). We have small script `bin/add_host_for_dev.sh` which alias this ip to `api.cpdb.me` if you like.

When provisioning is done, remember to generate initial data (run this inside VM):

```bash
./cpdb/manage.py cms_create_initial_data
```

For the development instance, do everything with `vagrant` user so that you don't have to deal with permission issues. Currently, you can choose how to develop the backend:
- You can use django development server by ssh to your vagrant instance and run `./manage.py runserver` or use `bin/start_dev.sh` script (need to turn off gunicorn for safety)
- If you like, current gunicorn on vagrant is configured to be reloadable, it will do the reload when your code changes, log will be outputted to file instead of console.

# Setup the production/staging

Our ansible scripts are production-ready. You can use them for automating your server setup steps. You only need to put your ssh keys to the server, we give you the small script name upload_ssh_keys.sh in bin folder which help you to transfer your ssh keys to the server (it will automatically change your filename to `id_rsa` and `id_rsa.pub`).

``` bash
bin/upload_ssh_keys.sh <your_ssh_key> <remote_user> <server_ip>
```

After that, you just need to run the `setup_staging` command and ansbile will help you to do the rest.
``` bash
bin/setup_staging
```

# Deployment

If you already setup your infrastructure with ansible, you can run deploy everytime by:

``` bash
bin/deploy_staging
```
Since deploy_staging command will NOT rebuild_index since it take great time. We recommend one should ssh to staging then 
run `rebuild_index` separately with specific doc_type

Currently, we are using azure blob storage to serve our heatmap cluster. In order to make the heatmap cluster available you will need to run the upload command:
```
cpdb/manage.py upload_heatmap_geojson
```

In fact, our CircleCI is currently set up to automatically deploy the `staging` branch. In cases where the feature being merged into staging requires rebuilding the
Elasticsearch index, you must tell the deploy script to do so by including `[rebuild_index]` in the merge commit's message:

```bash
# Do work on feature branch, commit & push as usual:
git commit
git push
# Checkout staging and merge said branch:
git checkout staging && git pull
git merge feature/my-feature-branch  # merge commit message editor opens - include `[rebuild_index]` here
git push  # remember to test locally before pushing of course!
```
**NOTE:** `[rebuild_index]` will rebuild ALL index, so it take 6 hours and impossible for CI to finish task. 
We suggest that commit message should specific which doc_type should be rebuild; i.e. 
``` Commit Message
[c] 000 - Some commit description here
[rebuild_index officers.officer_percentile_doc_type officers.officer_metrics_doc_type units]
```


# Update Docker images

We're using CircleCI version 2.0. As thus has moved on to running tests and deployment via Docker images. After you make changes to the Docker files, bump up the version and run following commands:

```
docker login
docker build -t cpdbdev/cpdbv2_backend:0.1.0 .circleci/docker
docker push cpdbdev/cpdbv2_backend:0.1.0
docker build -t cpdbdev/postgis:9.6-alpine .circleci/postgis-docker
docker push cpdbdev/postgis:9.6-alpine
```

# Keep secrets with git-secret

Please read instructions at http://git-secret.io/ to understand how it work. We have a few files encrypted this way. Generate a gpg key and give it's public key to your teammate to access those files.

# Managed infrastructure with Terraform

Get started by running these commands:

- `az login`
- `terraform init`
- `terraform refresh`

# Kubernetes

To interact with our kubernetes cluster via command line:

- [install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- `echo "$(terraform output kube_config)" > ./azurek8s`
- `export KUBECONFIG=./azurek8s`
- Now you should be able to run all kubectl commands such as `kubectl get nodes`

# Azure database for PostgreSQL

After you have access to git secrets and refreshed terraform, there are 2 commands that will make working with PostgreSQL easier:

- `bin/initialize_database.sh` Initialize database on staging or production. Can optionally provide a SQL dump file. Type `bin/initialize_database.sh -h` to read usage.
- `bin/psql.sh`: Quickly launch PostgreSQL terminal to access staging or production database. Type `bin/psql.sh -h` to read usage.

# Backup and Restore Elastic Search snapshot
## Backup
On local enviroment of elasticsearch:
```
curl -X PUT "localhost:9200/_snapshot/cpdp_es/snapshot_1?wait_for_completion=true" & tar -cvzf es_snapshot.tar.gz /backup/cpdp_es/
```

## Restore
With zipped snapshot
```
tar -xvf es_snapshot.tar.gz -C /backup/cpdp_es/
curl -X POST "localhost:9200/_snapshot/cpdp_es/snapshot_1/_restore"
```

# Removed apps

The following apps are removed: `landing_page`, `story`. Therefore if you come upon PostgreS tables that begin with `landing_page_` or `story_`, it should be safe to remove them.

# Infrastructure changes

For any infrastructure changes, please add a new Ansible role to set it up. Changes that are needed to run every deployment, please put the tag `deploy`.

For any changes in infrastructures, please put it into `Notes` section of the pull request.

Regarding to the nginx changes, please update both files: with and without https.

# Documentation
- [API standards](docs/api-standards.md)

# Miscelaneous

- [Snapshot test](docs/snapshot-test.md)
- [Visual tokens](docs/visual-tokens.md)
