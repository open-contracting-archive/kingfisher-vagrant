#!/bin/bash

set -e

echo "en_GB.UTF-8 UTF-8" >> /etc/locale.gen

locale-gen

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip postgresql-10 uwsgi apache2 libapache2-mod-proxy-uwsgi uwsgi-plugin-python3 supervisor redis graphviz openjdk-8-jre-headless libpq-dev

# Set up the database for remote access

echo "listen_addresses = '*'" >> /etc/postgresql/10/main/postgresql.conf
echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/10/main/pg_hba.conf
/etc/init.d/postgresql restart
sleep 5

# Download more software
# (Give database time to restart fully!)

pip3 install sphinx virtualenv

wget -O /bin/schemaspy.jar https://github.com/schemaspy/schemaspy/releases/download/v6.0.0/schemaspy-6.0.0.jar
wget -O /bin/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.2.5.jar

# Set up the database

sudo su --login -c "psql -c \"CREATE USER ocdskingfisher WITH PASSWORD 'ocdskingfisher';\"" postgres
sudo su --login -c "psql -c \"CREATE DATABASE ocdskingfisher WITH OWNER ocdskingfisher ENCODING 'UTF8'  LC_COLLATE='en_GB.UTF-8' LC_CTYPE='en_GB.UTF-8'  TEMPLATE=template0 ;\"" postgres
sudo su --login -c "psql -c \"CREATE SCHEMA views AUTHORIZATION ocdskingfisher ;\" ocdskingfisher" postgres

sudo su --login -c "psql -c \"CREATE USER test WITH PASSWORD 'test';\"" postgres
sudo su --login -c "psql -c \"CREATE DATABASE test WITH OWNER test ENCODING 'UTF8'  LC_COLLATE='en_GB.UTF-8' LC_CTYPE='en_GB.UTF-8'  TEMPLATE=template0 ;\"" postgres
sudo su --login -c "psql -c \"CREATE SCHEMA views AUTHORIZATION test ;\" test" postgres

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
echo "[REDIS]" >> /home/vagrant/.config/ocdskingfisher-process/config.ini
echo "HOST = localhost" >> /home/vagrant/.config/ocdskingfisher-process/config.ini

# Set up the Views config file

mkdir -p /home/vagrant/.config/ocdskingfisher-views

echo "[DBHOST]" > /home/vagrant/.config/ocdskingfisher-views/config.ini
echo "HOSTNAME = localhost" >> /home/vagrant/.config/ocdskingfisher-views/config.ini
echo "PORT = 5432" >> /home/vagrant/.config/ocdskingfisher-views/config.ini
echo "USERNAME = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-views/config.ini
echo "PASSWORD = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-views/config.ini
echo "DBNAME = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-views/config.ini


# Set up the Archive config file

mkdir -p /home/vagrant/.config/ocdskingfisher-archive

echo "[DBHOST]" > /home/vagrant/.config/ocdskingfisher-archive/config.ini
echo "HOSTNAME = localhost" >> /home/vagrant/.config/ocdskingfisher-archive/config.ini
echo "PORT = 5432" >> /home/vagrant/.config/ocdskingfisher-archive/config.ini
echo "USERNAME = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-archive/config.ini
echo "PASSWORD = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-archive/config.ini
echo "DBNAME = ocdskingfisher" >> /home/vagrant/.config/ocdskingfisher-archive/config.ini


cp /vagrant/vagrant/archive-logging.json /home/vagrant/.config/ocdskingfisher-archive/logging.json

chown -R vagrant /home/vagrant/.config


# Set up the Scrape config file

echo "#!/bin/bash" > /vagrant/scrape/env.sh
echo "export KINGFISHER_API_URI=http://localhost:9090" >> /vagrant/scrape/env.sh
echo "export KINGFISHER_API_KEY=cat" >> /vagrant/scrape/env.sh

chown vagrant /vagrant/scrape/env.sh


# Create and Install Virtual Environments

cd /vagrant/scrape
virtualenv .ve -p python3
source .ve/bin/activate;
# pip install can fail if .ve already exists, and we don't want errors to stop building totally. So always pass.
pip3 install -r requirements_dev.txt  || true
deactivate
chown -R vagrant /vagrant/scrape/.ve

cd /vagrant/process
virtualenv .ve -p python3
source .ve/bin/activate;
# pip install can fail if .ve already exists, and we don't want errors to stop building totally. So always pass.
pip3 install -r requirements_dev.txt  || true
KINGFISHER_PROCESS_DB_URI="postgresql://ocdskingfisher:ocdskingfisher@localhost:5432/ocdskingfisher" python ocdskingfisher-process-cli upgrade-database
deactivate
chown -R vagrant /vagrant/process/.ve

cd /vagrant/views
virtualenv .ve -p python3
source .ve/bin/activate;
# pip install can fail if .ve already exists, and we don't want errors to stop building totally. So always pass.
pip3 install -r requirements_dev.txt  || true
KINGFISHER_VIEWS_DB_URI="postgresql://ocdskingfisher:ocdskingfisher@localhost:5432/ocdskingfisher" PYTHONPATH="/vagrant/views:$PYTHONPATH"  alembic --raiseerr --config ocdskingfisherviews/alembic.ini upgrade head
deactivate
chown -R vagrant /vagrant/views/.ve

cd /vagrant/archive
virtualenv .ve -p python3
source .ve/bin/activate;
# pip install can fail if .ve already exists, and we don't want errors to stop building totally. So always pass.
pip3 install -r requirements_dev.txt  || true
deactivate
chown -R vagrant /vagrant/archive/.ve

# Set up Apache and UWSGI servers for people wanting to test on real servers
cp /vagrant/vagrant/apache.conf /etc/apache2/sites-enabled/kingfisherprocess.conf
a2enmod  proxy proxy_uwsgi proxy_http
systemctl stop apache2
systemctl disable apache2

cp /vagrant/vagrant/uwsgi.ini /etc/uwsgi/apps-enabled/kingfisherprocess.ini
cp /vagrant/vagrant/wsgi.py /vagrant/process/
systemctl stop uwsgi
systemctl disable uwsgi
