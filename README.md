


# Development

Please make sure that you have `vagrant 1.8.6` and `ansible 2.1.3.0` on your machine, we use them as isolated development environment and automation tools. After having both of these tools in your machine, you could start installing the ansible dependencies:

``` bash
ansible-galaxy install azavea.postgresql
```

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

# Removed apps

The following apps are removed: `landing_page`, `faq`, `story`. Therefore if you come upon PostgreS tables that begin with `landing_page_` or `faq_` or `story_`, it should be safe to remove them.

# Infrastructure changes

For any infrastructure changes, please add a new Ansible role to set it up. Changes that are needed to run every deployment, please put the tag `deploy`.

For any changes in infrastructures, please put it into `Notes` section of the pull request.

Regarding to the nginx changes, please update both files: with and without https.

# Documentation
- [API standards](docs/api-standards.md)

# Data pipeline

Going forward the only recommended way to import new data is to follow the following steps:

- Write database migrations as necessary. Do not write data migration.
- Produce fixtures to either insert new data or change existing data. A couple things:
    - Fixture file should be named like this: `<id>_<table_name>.json` (i.e. 001_investigator.json). `id` starts from "001" and increase each time a new fixture file is written. `id` should not collide with old ones of course, otherwise the fixture won't be applied.
    - You could produce the fixture file in any number of ways. But the recommended way for now is to create a notebook on http://cpdp-notebooks.southeastasia.cloudapp.azure.com/. Ask your teammate for credentials. Notebooks kept there must be named like this: `<date>_<name>.ipynb` (i.e. 20180109_Import_CMAP_data.ipynb)
- Test your fixture by running `cpdb/manage.py apply_fixtures` on local. It should only applied fixtures that haven't been applied.
- When you deploy to production or staging `apply_fixtures` is ran automatically.
- The applied fixtures can be checked by visiting admin page `/admin/data_pipeline/appliedfixture/`

# Miscelaneous

- [Snapshot test](docs/snapshot-test.md)
- [Visual tokens](docs/visual-tokens.md)
