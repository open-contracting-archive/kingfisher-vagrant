Hosted Kingfisher
=================

Open Contracting Partnership operates a hosted instance of the Kingfisher tool suite for the use of OCP staff and OCDS Team members. If you think you should have access to this, contact `<mailto:code@opendataservices.coop>`_.

Access
------

You can connect to the server via SSH to run commands, or via a Postgres client to run queries on the database. Details of this are below.

From time to time, we create development servers to try things out before deploying them. If you're involved in the development of new Kingfisher components, you may be asked to log into the dev server to try things out. If so, substitiute the address of the dev server you've been provided with for the address of the live server in the examples below.

Over the course of a typical use of Hosted Kingfisher, you'll need to log in to run scrapers, then log out and back in as a different user to run process operations, and potentially connect to Postgres to carry out database operations.

Access for kingfisher-scrape
----------------------------

kingfisher-scrape SSH access has been replaced by `kingfisher-collection scrapyd access <https://ocdsdeploy.readthedocs.io/en/latest/use/kingfisher-collect.html>`_.

Access for kingfisher-process
-----------------------------

If you're running process operations, SSH in as the *ocdskfp* user::

  ssh ocdskfp@process.kingfisher.open-contracting.org

Once logged in, you can run process operations as per the `kingfisher-process documentation <https://kingfisher-process.readthedocs.io/en/latest/cli/index.html>`_

You can `browse the information in the web UI. <http://process.kingfisher.open-contracting.org/app>`_

The tools available are:

* jq
* flatten-tool
* ocdskit

Access for analysis
-------------------

If you're running analysis operations, SSH in as the *analysis* user::

    ssh analysis@analyse.kingfisher.open-contracting.org

Once logged in, you can take advantage of the powerful server to carry out analysis operations, such as using flatten-tool on files, more quickly than on your local machine. The analysis user has read-only access to the files downloaded by the scrapers. Please remember to delete your files when you're done!

The tools available are:

* jq
* flatten-tool
* ocdskit

Transferring files between users
--------------------------------

Currently Scrape, Process and Analysis are all users on the same server.

If you want to transfer files between them, the easiest way is to make sure the user that owns the files makes them world readable. You can then copy them or read them directly from the other users.

First, make sure the files themselves are world readable::

    chmod a+r files.json

You also need to make sure the directory the files are in have the correct permissions to allow users to look inside them::

    chmod a+rx /home/user/path/to/files/

This must be set for all parent directories too::

    chmod a+rx /home/user/path/to/
    chmod a+rx /home/user/path/

Access to the archives
----------------------

There is an archive server which contains files that have been downloaded previously but are no longer held on the main server. In some cases, the data from them is still in the process database, but they are retained for reference. If you would like to access them, SSH in as the *archive* user::

    ssh archive@archive.kingfisher.open-contracting.org

Access for Postgres Database queries
------------------------------------

In order to access the database, you'll need a Postgres client such as `pgadmin <https://www.pgadmin.org/>`, and some details that are stored on the server.

To obtain the details, SSH into the server as the *ocdskfp* user (as above), and then run:::
  cat ~/.pgpass

The output contains two lines, for the two different database users that are available. It is recommended that you use the read-only user unless you're making changes to the database. The lines have the format:

localhost:*port*:*database*:*username*:*password*

These should be all the details you need to connect with a Postgres client.

**Querying the database using psql**

When connected to the kingfisher process server as the *ocdskfp* user, the `psql` command can be used to query the database from the command line.

To connect to the database use the following command::

    psql -d ocdskingfisherprocess -h localhost -U ocdskfpreadonly

To query the database, enter a query at the psql command prompt and **end it with the `;` character**::

    ocdskingfisherprocess=> select distinct source_id from collection;

Access for Redash
-----------------

A Redash server is available. Contact Open Data Services for access.
