# -*- mode: ruby -*-
# vi: set ft=ruby :

# This sets up an ubuntu 16.04 vm for use with ansible testing
Vagrant.configure(2) do |config|
  config.vm.box = "geerlingguy/ubuntu1604"
  config.vm.network "private_network", ip: "172.31.31.123", hostsupdater: "skip"
  config.vm.provider :virtualbox do |vb|
    vb.name = "crystalops"
    vb.memory = 1024
  end
end
