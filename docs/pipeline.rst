The Pipeline
============

The tool runs a pipeline of stages.

Gather Stage
------------

In this stage, the tool just gathers the URLs that will be downloaded in the next stage.

This stage is designed to be as short as possible. Some HTTP requests may be made at this point, but not many.
For this reason it was not designed to be resumable - if it stops half way through for any reason it must be restarted.

Note it is not guaranteed to find all the URL's at this stage - some may be found during the fetch stage.

Some sources are very simple - for instance taiwan and canada_buyandsell simply return a list of hard coded URL's.

Some sources are more complex - for instance uk_contracts_finder will make one request. In the results of that request
it will look up what the maximum number of pages is (the API is paginated).
With that knowledge, it can generate a full list of URL's to download.

Fetch Stage
-----------

In this stage, the tool downloads all the URL's it can and saves them to disk.

This stage may take a very long time. For that reason, it is designed to be resumable.
If it is stopped half way through it can be restarted.

Note as well as downloading the URL, specific sources may do more at this stage.
Sometimes, we can download one URL and then extract other URL's we need to download from that data.

These new URL's are then added to the list of current URL's.
(One side affect of this is that the count of files downloaded and to download may be inaccurate.
For instance, a process may say "downloaded 15 of 20 URL's".
But then, when downloading and processing URL number 16, it may find another 10 URL's to download.
The process would then say "downloaded 16 of 30 URL's".)

An example of a source that does not do this is uk_contracts_finder - this just downloads the URL and saves it to disk.

An example of a source that does do this is ukraine - sometimes this downloads webpages with lists of data,
and from them it extracts the actual URL of the data to download.

Store Stage
-----------

In this stage, the tool simply takes the data from disk and stores it in the database.

This stage may take a long time. For that reason, it is designed to be resumable.
If it is stopped half way through it can be restarted.

Check Stage
-----------

In this stage, the tool takes the data in the database and checks it using the same checks as CoVE.
The results are stored in the database.

This stage may take a long time. For that reason, it is designed to be resumable.
If it is stopped half way through it can be restarted.

Additional stages - check against a different schema version
------------------------------------------------------------

You can also select this additional stage manually.

This stage lets you take the data in the database,
and then pretend the data is of a different schema version. It is then checked using the same checks as CoVE.

See :doc:`cli-check-different-schema-version` for more details.

This stage may take a long time. For that reason, it is designed to be resumable.
If it is stopped half way through it can be restarted.
