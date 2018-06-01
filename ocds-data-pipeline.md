OCDS Data Pipeline
==================

`ocdsdata` is part of a pipeline to obtain OCDS data from publishers and prepare it for use by analysts who wish to understand the state of the data.

Traditionally, this would be referred to as an 'ETL pipeline', however the nuances of the OCDS data ecosystem meant that distinct Extract / Transform / Load stages weren't appropriate. The major stages of the pipeline are outlined here:

Gather
------

The first step is to obtain a list of all the URLs where OCDS data can be found, and to work out what form it's in. The logic to do this lives in Source files - see https://github.com/open-contracting/ocdsdata/tree/master/ocdsdata/sources

Current status: Implemented

Fetch
-----

Once we have the URLs, we can obtain the raw data. This is downloaded from the URLs to files on disk. We also keep status information at this stage about failed downloads.

Current status: Implemented

Load
----

Once the files have been downloaded, they are loaded into Postgres in a raw format - there are tables for releases and records, containing blobs of JSON

Current status: Implemented

Normalise
---------

How OCDS data is normalised depends on use case. We use JSON selects to query the JSON blobs and create new, normalised tables.

Current status: Under active development as of May 2018

Analyse
-------

The data can then be analysed. We typically use Redash to create dashboards to give an overview of the data, backed by SQL queries.

Current status: Not yet implemented. Currently this work happens on an ad-hoc basis
