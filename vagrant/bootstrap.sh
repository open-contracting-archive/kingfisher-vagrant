#!/bin/bash

set -e

echo "en_GB.UTF-8 UTF-8" >> /etc/locale.gen

locale-gen

apt-get update
apt-get install -y python3 python3-pip postgresql-10 uwsgi apache2 libapache2-mod-proxy-uwsgi uwsgi-plugin-python3 supervisor redis graphviz openjdk-8-jre-headless libpq-dev

pip3 install sphinx virtualenv

wget -O /bin/schemaspy.jar https://github.com/schemaspy/schemaspy/releases/download/v6.0.0/schemaspy-6.0.0.jar
wget -O /bin/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.2.5.jar

# Set up the database

sudo su --login -c "psql -c \"CREATE USER ocdskingfisher WITH PASSWORD 'ocdskingfisher';\"" postgres
sudo su --login -c "psql -c \"CREATE DATABASE ocdskingfisher WITH OWNER ocdskingfisher ENCODING 'UTF8'  LC_COLLATE='en_GB.UTF-8' LC_CTYPE='en_GB.UTF-8'  TEMPLATE=template0 ;\"" postgres

sudo su --login -c "psql -c \"CREATE USER test WITH PASSWORD 'test';\"" postgres
sudo su --login -c "psql -c \"CREATE DATABASE test WITH OWNER test ENCODING 'UTF8'  LC_COLLATE='en_GB.UTF-8' LC_CTYPE='en_GB.UTF-8'  TEMPLATE=template0 ;\"" postgres


echo "alias db='psql -U  ocdskingfisher ocdskingfisher  -hlocalhost'" >> /home/vagrant/.bashrc
echo "localhost:5432:ocdskingfisher:ocdskingfisher:ocdskingfisher" > /home/vagrant/.pgpass
chown vagrant:vagrant /home/vagrant/.pgpass
chmod 0600 /home/vagrant/.pgpass

# Set up the Process config file

mkdir -p /home/vagrant/.config/ocdskingfisher-process

echo "[DBHOST]" > /home/vagrant/.config/ocdskingfisher-process/config.ini
echo "HOSTNAME = localhost" >> /home/vagrant/.config/ocdskingfisher-process/config.ini
echo "PORT = 5432" >> /home/vagrant/.config/ocdskingfisher-process/config.ini
echo "USERNAME = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-process/config.ini
echo "PASSWORD = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-process/config.ini
echo "DBNAME = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-process/config.ini
echo "[WEB]" >> /home/vagrant/.config/ocdskingfisher-process/config.ini
echo "API_KEYS = cat,dog" >> /home/vagrant/.config/ocdskingfisher-process/config.ini

chown -R vagrant /home/vagrant/.config


# Set up the Scrape config file

echo "#!/bin/bash" > /scrape/env.sh
echo "export KINGFISHER_API_URI=http://localhost:9090" >> /scrape/env.sh
echo "export KINGFISHER_API_KEY=cat" >> /scrape/env.sh

chown vagrant /scrape/env.sh

# Create and Install Virtual Environments

cd /scrape
virtualenv .ve -p python3
source .ve/bin/activate;
pip3 install -r requirements_dev.txt
deactivate
chown -R vagrant /scrape/.ve

cd /process
virtualenv .ve -p python3
source .ve/bin/activate;
pip3 install -r requirements.txt
pip3 install flake8 pytest
deactivate
chown -R vagrant /process/.ve

cd /views
virtualenv .ve -p python3
source .ve/bin/activate;
##### This file doesn't exist yet but when it does .... pip3 install -r requirements.txt
deactivate
chown -R vagrant /views/.ve


# Set up Apache and UWSGI servers for people wanting to test on real servers
cp /vagrantconf/apache.conf /etc/apache2/sites-enabled/kingfisherprocess.conf
a2enmod  proxy proxy_uwsgi proxy_http
systemctl stop apache2
systemctl disable apache2

cp /vagrantconf/uwsgi.ini /etc/uwsgi/apps-enabled/kingfisherprocess.ini
cp /vagrantconf/wsgi.py /process/
systemctl stop uwsgi
systemctl disable uwsgi

