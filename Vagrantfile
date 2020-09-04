# -*- mode: ruby -*-
# vi: set ft=ruby :
#
# Docs at https://ocdskingfisher.readthedocs.io/en/latest/vagrant.html

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/xenial64"

    config.vm.define "ocds-kingfisher" do |normal|

        normal.vm.box = "ubuntu/bionic64"

        normal.vm.network "forwarded_port", guest: 8080, host: 8080
        normal.vm.network "forwarded_port", guest: 9090, host: 9090
        normal.vm.network "forwarded_port", guest: 5432, host: 7070

        normal.vm.synced_folder ".", "/vagrant",  :owner=> 'vagrant', :group=>'users', :mount_options => ['dmode=777', 'fmode=777']

        normal.vm.provider "virtualbox" do |vb|
          # Some versions of VB have a length limit, and some version of Vagrant try and set a name that is to long
          # So set one explicitly 
          vb.name = "ocds-kingfisher"

           # Display the VirtualBox GUI when booting the machine
           vb.gui = false

          # Customize the amount of memory on the VM:
          vb.memory = "2048"

          # https://github.com/boxcutter/ubuntu/issues/82#issuecomment-260902424
          vb.customize [
              "modifyvm", :id,
              "--cableconnected1", "on",
          ]

        end

        normal.vm.provision :shell, path: "vagrant/bootstrap.sh"

    end

end
