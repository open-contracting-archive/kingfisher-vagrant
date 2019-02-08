Hosted Kingfisher
=================

Open Contracting Partnership operates a hosted instance of the Kingfisher tool suite for the use of OCP staff and OCDS Team members. If you think you should have access to this, contact `<mailto:code@opendataservices.coop>`_.

Access
------

The server can be found at 195.201.163.242. You can connect via SSH to run commands, or via a Postgres client to run queries on the database (see below)

From time to time, we create development servers to try things out before deploying them. If you're involved in the development of new Kingfisher components, you may be asked to log into the dev server to try things out. If so, substitiute the address of the dev server you've been provided with for the address of the live server in the examples below. 

Over the course of a typical use of Hosted Kingfisher, you'll need to log in to run scrapers, then log out and back in as a different user to run process operations, and potentially connect to Postgres to carry out database operations. 


Access for kingfisher-scrape
----------------------------

If you're running scrapers, SSH in as the *ocdskfs* user::

  ssh ocdskfs@195.201.163.242

Once logged in, you can run scrapers as per the `kingfisher-scrape documentation <https://kingfisher-scrape.readthedocs.io/en/latest/use-hosted.html>`_


Access for kingfisher-process
-----------------------------

If you're running process operations, SSH in as the *ocdskfp* user::

  ssh ocdskfp@195.201.163.242

Once logged in, you can run process operations as per the `kingfisher-process documentation <https://kingfisher-process.readthedocs.io/en/latest/cli.html>`_

Access for Postgres Database queries
------------------------------------

In order to access the database, you'll need a Postgres client such as `pgadmin <https://www.pgadmin.org/>`, and some details that are stored on the server. 

To obtain the details, SSH into the server as the *ocdskfp* user (as above), and then run:::
  cat ~/.pgpass

The output contains two lines, for the two different database users that are available. It is recommended that you use the read-only user unless you're making changes to the database. The lines have the format:

localhost:*port*:*database*:*username*:*password*

These should be all the details you need to connect with a Postgres client.


Access for Redash
-----------------

A Redash server is available. Contact Open Data Services for access. 
