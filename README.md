


# Development

Please make sure that you have `vagrant 1.8.6` and `ansible 2.1.3.0` on your machine, we use them as isolated development environment and automation tools. After having both of these tools in your machine, you could start installing the ansible dependencies:

``` bash
ansible-galaxy install azavea.postgresql
git clone git@github.com:CyVerse-Ansible/ansible-elasticsearch-1.git
sudo mv -r ansible-elasticsearch-1 /etc/ansible/roles/cyverse.elasticsearch
```

Ask the team for the ansible vault password, then put it in a text file at `../vault_pass.txt` (parent dir of this repo).

Then just `vagrant up --provision` and wait for ansible to do its things. When the provision is done, you may find your application running at ip `192.168.50.100` (you can change them in `Vagrantfile`). We have small script `bin/add_host_for_dev.sh` which alias this ip to `api.cpdb.me` which you can use it for more convenient on development.

When ansible is done, remember to generate initial data (run this inside VM):

```bash
./cpdb/manage.py cms_create_initial_data
```

For the development instance, it's better to use all the `vagrant` user to make it less effort dealing with permission. Currently, we have both options for you to choose how to develop the backend:
- You can use django development server by ssh to your vagrant instance and run `./manage.py runserver` (need to turn off gunicorn for safety)
- If you like, current gunicorn on vagrant is configured to be reloadable, it will do the reload when your code changes, but you need to read the log yourselves.

No need to run `vagrant rsync-auto` anymore since we're using default synced folder strategy.

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

For any infrastructure changes, please add a new roles in ansible stuff to set it up. With the changes that you want to use it for deployment, let it come with the tags `deploy`.

For any changes in infrastructures, please note it into `Notes` section of the pull request.

Regarding to the nginx changes, please update both of the files, https one and http one.

# Documentation
- [API standards](docs/api-standards.md)

# Import data from v1
- Export v2 data:
    + Run `./manage.py export_all_data_for_v2` on v1 repository (**Note:** Base on new v2 model you may need to modify this script).
    + Data from v1 will be exported into csv files in root folder after run above command.
- Import v2 data: Run `cpdb/manage.py import_002_officer_data_from_v1 --folder [FOLDER]` on v2 repository.
- After importing run: `cpdb/manage.py rebuild_index` to rebuild indexes for elasticsearch.
