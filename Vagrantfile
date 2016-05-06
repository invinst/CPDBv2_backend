# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "private_network", ip: "192.168.50.100"
  # config.vm.synced_folder ".", "/webapps/cpdb", owner: "deploy", group: "deploy"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/vagrant.yml"
    ansible.host_key_checking = false
    ansible.verbose = "v"
  end
end
