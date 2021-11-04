# -*- mode: ruby -*-
# vi: set ft=ruby :

dir = File.dirname(File.expand_path(__FILE__))
settings = YAML::load_file("#{dir}/vagrant-defaults.yml")

if File.exist?("#{dir}/vagrant-local.yml")
    env_settings = YAML::load_file("#{dir}/vagrant-local.yml")
    settings.merge!(env_settings)
end

Vagrant.configure(2) do |config|
    config.vm.hostname = "crystalops"
    config.vm.box = "ubuntu/focal64"
    config.vm.network "private_network", ip: settings['ops_ip'], hostsupdater: settings['ops_hostsupdater']
    config.vm.synced_folder ".", "/vagrant", disabled: true
    config.vm.provider :virtualbox do |vb|
        vb.name = "crystalops"
        vb.memory = settings['ops_memory'] || 2048
    end

	if settings['ops_provision'] != false
		config.vm.provision "ansible" do |ansible|
			ansible.playbook = "plays/bootstrap.yml"
			ansible.groups = {
				all: ["vagrants"],
				vagrants: ["default"]
			}
			ansible.extra_vars = {
				hostip: "default",
				user: "vagrant"
			}
		end
	end

	# Allow an untracked Vagrantfile to modify the configurations
	eval File.read "#{dir}/Vagrantfile.local" if File.exist?("#{dir}/Vagrantfile.local")
end
