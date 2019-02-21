Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/xenial64"

    config.vm.define "open-contracting-kingfisher" do |normal|

        config.vm.box = "ubuntu/bionic64"

        config.vm.network "forwarded_port", guest: 9090, host: 9090

        config.vm.synced_folder "process/", "/process",  :owner=> 'vagrant', :group=>'users', :mount_options => ['dmode=777', 'fmode=777']
        config.vm.synced_folder "scrape/", "/scrape",  :owner=> 'vagrant', :group=>'users', :mount_options => ['dmode=777', 'fmode=777']
        config.vm.synced_folder "views/", "/views",  :owner=> 'vagrant', :group=>'users', :mount_options => ['dmode=777', 'fmode=777']
        config.vm.synced_folder "vagrant/", "/vagrantconf",  :owner=> 'vagrant', :group=>'users', :mount_options => ['dmode=777', 'fmode=777']


        config.vm.provider "virtualbox" do |vb|
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

        config.vm.provision :shell, path: "vagrant/bootstrap.sh"

    end

end
