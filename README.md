


# Development

Please make sure that you have `vagrant 1.8.6` and `ansible 2.1.3.0` on your machine, we use them as isolated development environment and automation tools. After having both of these tools in your machine, you could start installing the ansible dependencies:

``` bash
ansible-galaxy install azavea.postgresql
```

Ask the team for the ansible vault password, then put it in a text file at `../vault_pass.txt` (parent dir of this repo). This file is used to decrypt ansible variables contained in `ansible/env_vars/secrets.yml` and `ansible/env_vars/vagrant-secrets.yml` files.

Ansible variables in `ansible/env_vars/secrets.yml` and `ansible/env_vars/vagrant-secrets.yml` files:
- `ssl_key_password`: password for ssl key
- `ssl_crt`: ssl certificate
- `ssl_key`: ssl key
- `db_user`: Database user name
- `db_name`: Database name
- `db_password`: Database password
- `env_file`: A multiline string with the same format in `env.sample` file which contains following environment variables:
    - `DJANGO_SETTINGS_MODULE`: Django settings module
    - `DJANGO_DEBUG`: Debug mode
    - `DATABASE_URL`: Database url
    - `DJANGO_SECRET_KEY`: Django secret key
    - `MAILCHIMP_API_KEY`: Mailchimp api key
    - `MAILCHIMP_USER`: Mailchimp user name
    - `AZURE_STORAGE_ACCOUNT_NAME`: Azure storage account name
    - `AZURE_STORAGE_ACCOUNT_KEY`: Azure store account key
    - `MAILGUN_API_KEY`: Mailgun api key
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

# Infrastructure changes

For any infrastructure changes, please add a new Ansible role to set it up. Changes that are needed to run every deployment, please put the tag `deploy`.

For any changes in infrastructures, please put it into `Notes` section of the pull request.

Regarding to the nginx changes, please update both files: with and without https.

# Documentation
- [API standards](docs/api-standards.md)

# Import data from v1
- Export v2 data:
    + Run `./manage.py export_all_data_for_v2` on v1 repository (**Note:** Base on new v2 model you may need to modify this script).
    + Data from v1 will be exported into csv files in root folder after run above command.
- Import v2 data: Run `cpdb/manage.py import_002_officer_data_from_v1 --folder [FOLDER]` on v2 repository.
- After importing run: `cpdb/manage.py rebuild_index` to rebuild indexes for elasticsearch.
