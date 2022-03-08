# -*- mode: ruby -*-
# vi: set ft=ruby :

SITE = "macrobatics"
HOSTNAME = "ubuntu-#{SITE}"
VAGRANT_HOME = "/home/vagrant"
SITE_DIR = "#{VAGRANT_HOME}/site"
PROJECT_DIR = "#{SITE_DIR}/proj/#{SITE}"
VENV_DIR = "#{SITE_DIR}/envs"

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'virtualbox'

Vagrant.configure("2") do |config|
  ##### DEFINE VM #####
  config.vm.define HOSTNAME do |config|
  config.vm.hostname = HOSTNAME
  config.vm.box = "generic/ubuntu1804"
  config.vm.box_check_update = false
  config.vm.network "private_network", ip: "172.31.0.4"
  config.vm.provision "file", source: "env/id_rsa", destination: "/home/vagrant/.ssh/id_rsa"
  config.vm.provision "file", source: "env/init.vim", destination: "/home/vagrant/.config/nvim/init.vim"
  config.vm.provision "file", source: "env/bashrc", destination: "/home/vagrant/.bashrc"
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt update
    sudo apt -y upgrade

    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

    echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee
  /etc/apt/sources.list.d/pgdg.list

    sudo apt update
    sudo apt -y install postgresql-12 postgresql-client-12 libpq-dev

    sudo apt install software-properties-common -y
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt install python3.7 -y
    sudo apt install python3-pip python3.7-venv pkg-config python3.7-dev build-essential python-setuptools python-wheel -y


    sudo mkdir -p #{SITE_DIR}
    sudo mkdir -p #{VENV_DIR}
    cd #{VENV_DIR}
    python3.7 -m venv #{SITE}
    sudo mkdir -p #{PROJECT_DIR}
    sudo chown -R vagrant:vagrant #{SITE_DIR}
  SHELL
  config.vm.network :forwarded_port, host: 8004, guest: 8000
  config.vm.network :forwarded_port, host: 8886, guest: 8888
  end
end
