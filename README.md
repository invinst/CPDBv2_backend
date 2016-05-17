[![Coverage Status](https://coveralls.io/repos/EastAgile/CPDBv2_backend/badge.svg?branch=master)](https://coveralls.io/github/EastAgile/CPDBv2_backend?branch=master)

* Development
We use `vagrant` for isolated development environment, you can install it from [here](..). First of all, you needs to install needed roles:

``` bash
ansible-galaxy install azavea.postgresql
```

Then, start your vagrant box with the ansible-vault password path to be supplied:

``` bash
ANSIBLE_VAULT_PASSWORD_FILE=<your-ansible-vault-password> vagrant up
```

If you are lazy, you can use the packaged box [here](...).
After registering the box to vagrant

``` bash
vagrant add cpdb cpdb.box
```

then creating the new Vagrantfile:

``` ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "cpdb"
  config.vm.network "private_network", ip: "192.168.50.100"
  config.vm.synced_folder ".", "/webapps/cpdb", owner: "deploy", group: "deploy"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/vagrant.yml"
    ansible.host_key_checking = false
    ansible.verbose = "v"
  end
end
```
