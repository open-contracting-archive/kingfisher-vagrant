OCDS Kingfisher tool
====================

OCDS Kingfisher is a suite of tools for downloading, storing and analysing data from publishers of the Open Contracting Data Standard.

Overview
--------

Kingfisher comprises three tools, which integrate to form an OCDS data pipeline:

- `kingfisher-scrape <https://github.com/open-contracting/kingfisher-scrape>`_ , for downloading data from public sources of OCDS data
- `kingfisher-process <https://github.com/open-contracting/kingfisher-process>`_, for storing OCDS data, and performing operations on it, including transformation and validation. 
- A suite of queries that can be used to meaningfully interpret OCDS data sets

![kingfisher-model](images/kingfisher_model.png)

In the model you can see "Kingfisher Scrape" retrieves the data and stores it in a server, then "Kingfisher Process" puts them in the database in JSON format and also makes transformations, and "views" transform the jsons into their tabulated format to finally use them for generate the graphics.


Hosted Kingfisher
-----------------

Kingfisher has been developed primarily for internal use by Open Contracting Partnership, and OCP maintains a hosted instance. If you work or OCP or are part of the OCDS Team, see :doc:`hosted` for details of the server, and how to access it. 

Previous Versions
-----------------

In Febrary 2019, Kingfisher was completely rewritten. You can find details of previous versions on the :doc:`old` page.


Typical Uses of Kingfisher in the OCDS Helpdesk
-----------------------------------------------

I'm helping a publisher who's just published for the first time understand the quality of their data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, write a scraper for the new source, or ask one of the developers to do it. 
Once it's merged into master on kingfisher-scrape, deploy the updated code to the server (using salt), and then log into the server and run the new scraper
After a few minutes, check on the status of the scraper. Once it's started downloading, you should be able to open a connection to the Postgres database and see the data coming in. 

Typical Uses of Kingfisher outside of the OCDS Helpdesk
-------------------------------------------------------

I'm a journalist interested in my country's OCDS data, and I want to be able to download the whole data set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, check that kingfisher-scrape has a scraper for your country. If not, email data@open-contracting.org to let us know about the data. Then, install kingfisher-scrape, and run it to download the data. If you already have your own database, you can import the downloaded files to it. Or, if you'd prefer, you can use kingfisher-process to store the data in a Postgres database directly from the scraper.

I'm helping a government publish OCDS data, and I want to check that the published data is correct
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the data is already online, then use kingfisher-scrape to download it from the public portal. Email data@open-contracting.org if you require assistance with this. If the data isn't online, but you have it as JSON files on disk, you can use kingfisher-process to import it into a Postgres database, and then use the provided queries to start to understand the data. 


Other Information
-----------------

.. toctree::

   hosted.rst
   old.rst
   vagrant.rst

