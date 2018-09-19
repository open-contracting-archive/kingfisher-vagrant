Command line tool - check-different-schema-version option
=========================================================

In the check stage of the pipeline, the data will be checked against the most appropriate version of the standard.

In most cases, this will just be the version reported in the data.
(One source gets data with a badly reported source, and in that case the version is corrected to the intended one.)

You may want to check the data against a different schema version - for example you may have some `1.0` data and want
to check it against the `1.1` schema version.

The check-different-schema-version command does this.

Note it does not upgrade the data properly; the only change it makes is to change the version field in the data to
the version you specify.

You must specify the source you want as the first argument. You can also include the `sample` flag.

.. code-block:: shell-session

    python ocdskingfisher-cli check-different-schema-version taiwan
    python ocdskingfisher-cli check-different-schema-version taiwan --sample

It will look for existing sessions for the same source and sample flag as you specify, and by default check the latest one.

To select a specific existing session, pass the `dataversion` flag.

.. code-block:: shell-session

    python ocdskingfisher-cli check-different-schema-version --dataversion 2018-07-31-16-03-50 ...

By default, it will convert to the latest version of the schema, but you can change that with the `schemaversion` option.

.. code-block:: shell-session

    python ocdskingfisher-cli check-different-schema-version --schemaversion 1.0 ...


