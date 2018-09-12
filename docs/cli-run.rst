Command line tool - run option
==============================

The run command actually runs the pipeline.

Run it by passing the name of one or more sources to run:

.. code-block:: shell-session

    python ocdskingfisher-cli run taiwan
    python ocdskingfisher-cli run taiwan canada_buyandsell

You can run all sources with the `all` flag.

.. code-block:: shell-session

    python ocdskingfisher-cli run --all

It is not recommended to do this as some of the sources take a very long time to download!

There is a sample mode. This only fetches a small amount of data for each source.
(If you use the `all` flag we strongly recommend the `sample` flag to!)

.. code-block:: shell-session

    python ocdskingfisher-cli run --sample ...

It will look for existing sessions for the same source and sample flag as you specify, and by default resume the latest one.

To make sure you start a new session, pass the `newversion` flag.

.. code-block:: shell-session

    python ocdskingfisher-cli run --newversion  ...

To select an existing session, pass the `dataversion` flag.

.. code-block:: shell-session

    python ocdskingfisher-cli run --dataversion 2018-07-31-16-03-50 ...

By default, it will run all stages of the pipeline.

You can specify that only one stage should be run with the following flags:

  *  onlygather
  *  onlyfetch
  *  onlystore
  *  onlycheck

You can specify that stages should be skipped with the following flags:

  *  ignoregather
  *  ignorefetch
  *  ignorestore
  *  ignorecheck

For example:

.. code-block:: shell-session

    python ocdskingfisher-cli run --skipstore --skipcheck ...
