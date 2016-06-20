


# Development

Please make sure that you have `vagrant` and `ansible` on your machine, we use them as isolated development environment and automation tools. After having both of these tools in your machine, you could start installing the ansible dependencies:

``` bash
ansible-galaxy install azavea.postgresql
```

Then up your vagrant box
``` bash
vagrant up
```

It will ask you the password for ansible-vault, then you only need to wait for a while until ansible do all the needed stuff. When the provision is done, you may find your application running at ip `192.168.50.100` (you can change them in `Vagrantfile`). We have small script `bin/add_host_for_dev.sh` which alias this ip to `api.cpdb.me` which you can use it for more convenient on development.

For the development instance, it's better to use all the `vagrant` user to make it less effort dealing with permission. Currently, we have both options for you to choose how to develop the backend:
- You can use django development server by ssh to your vagrant instance and run `./manage.py runserver` (need to turn off gunicorn for safety)
- If you like, current gunicorn on vagrant is configured to be reloadable, it will do the reload when your code changes, but you need to read the log yourselves.
- 
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
