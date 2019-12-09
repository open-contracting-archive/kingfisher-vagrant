Vagrant for developers
----------------------

A Vagrant box is included in this repository. This is one box that includes Scrape and Process for any development work.

Requirements
============

You will need:

  *  Vagrant https://www.vagrantup.com/
  *  VirtualBox https://www.virtualbox.org/

(It may be possible to get this to work with other Virtulisation solutions, but VirtualBox is the one we have tested with. Also check your virtualization options to make the system work, if you are already virtualizing your server you may have problems with starting Vagrant)

Setting up repositories
=======================

To use it, check out the main repository somewhere on your disk.

 .. code-block:: shell-session

    git clone git@github.com:open-contracting/kingfisher.git somewhere_you_decide

You then need to check out the repositories with the actual code. Note these must be within the location you just created - so change to that folder. Also use the names specified here, as the Vagrantfile will refer to these.

 .. code-block:: shell-session

    cd somewhere_you_decide
    git clone git@github.com:open-contracting/kingfisher-scrape.git scrape
    git clone git@github.com:open-contracting/kingfisher-process.git process
    git clone git@github.com:open-contracting/kingfisher-views.git views

Starting and building the Vagrant box
=====================================

Simply type

 .. code-block:: shell-session

    vagrant up

Opening (and exiting) a shell in the Vagrant box
================================================

Simply type

 .. code-block:: shell-session

    vagrant ssh

To exit this shell, type `exit`.

Working with Scrape
===================

You will find all the files inside the vagrant box in `/scrape`

There is a virtual environment at `.ve`

So, after you have opened a shell inside the Vagrant box, try:

Simply type

 .. code-block:: shell-session

    cd /scrape
    source .ve/bin/activate

You can run standalone Scrapy commands straight away - see https://kingfisher-scrape.readthedocs.io/en/latest/use-standalone.html

Working with Process
====================

You will find all the files inside the vagrant box in `/process`

There is a virtual environment at `.ve`

So, after you have opened a shell inside the Vagrant box, try:

 .. code-block:: shell-session

    cd /process
    source .ve/bin/activate

You can access the database by simply typing `db`.

There is a test database  - to run tests in try:

 .. code-block:: shell-session

    KINGFISHER_PROCESS_DB_URI=postgresql://test:test@localhost:5432/test pytest tests/

To run the app in debug mode on port 9090, try:

 .. code-block:: shell-session

    FLASK_APP=ocdskingfisherprocess.web.app FLASK_ENV=development KINGFISHER_PROCESS_WEB_API_KEYS=cat flask run --host 0 --port 9090

When this is running, you should be able to see results in http://localhost:9090/app

You can generate a detailed description of the database Schema with SchemaSpy:

 .. code-block:: shell-session

    java -jar /bin/schemaspy.jar -t pgsql -dp /bin/postgresql.jar   -s public  -db ocdskingfisher  -u ocdskingfisher -p ocdskingfisher -host localhost -o /vagrant/schemaspy

Working with Views
==================

You will find all the files inside the vagrant box in `/views`

There is a virtual environment at `.ve`

More information will follow soon. TODO

Working with Apache and UWSGI servers
=====================================

These are the servers used on live, and you may need to check something on them instead of using the Flask development server.

These are installed and configured and just need to be started:

 .. code-block:: shell-session

    sudo /etc/init.d/uwsgi start
    sudo /etc/init.d/apache2 start

Then browse at http://localhost:8080/app

Guide: Running a scraper and seeing it appear in the database
=============================================================

You will need two shells open.

In the first one, we are going to run the process app:

 .. code-block:: shell-session

    cd /process
    source .ve/bin/activate
    python ocdskingfisher-process-cli upgrade-database
    FLASK_APP=ocdskingfisherprocess.web.app FLASK_ENV=development KINGFISHER_PROCESS_WEB_API_KEYS=cat flask run --host 0 --port 9090

Leave that running.

Open a second shell and run:

 .. code-block:: shell-session

    cd /scrape
    source .ve/bin/activate
    source env.sh
    scrapy crawl canada_buyandsell -a sample=true

Log messages will appear in the shell. While this is happening, you can

* Open a third shell, type `db` and see the data appear in the database
* Open a webbrowser, and see the data appear in http://localhost:9090/app

Finishing work with the Vagrant Box
===================================

Simply type

 .. code-block:: shell-session

    vagrant halt

If you break the Vagrant Box
============================

If you have tried to change the config of the software, tried to install something else and it's all gone horribly wrong ....

That's totally fine!

The whole point is there should be no data you care about inside the Vagrant box, and thus you should feel free to destroy it and recreate it at any time.

 .. code-block:: shell-session

    vagrant destroy
    vagrant up

Removing totally the Vagrant Box
================================

Simply type

 .. code-block:: shell-session

    vagrant destroy
