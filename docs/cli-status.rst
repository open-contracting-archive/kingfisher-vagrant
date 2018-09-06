Command line tool - status option
=================================


During or after a run you can use the status command to check on the progress.

Run `ocdskingfisher-cli status` with the source as the publisher you want to see. Pass the sample flag too, if it's a sample run.


.. code-block:: shell-session

    python ocdskingfisher-cli status taiwan
    python ocdskingfisher-cli status --sample taiwan


By default it will show the progress for the latest run, but you can pass the dataversion flag to see a specify version.


.. code-block:: shell-session

    python ocdskingfisher-cli status --dataversion  2018-07-31-16-03-50 ...


The tool will load files from disk. To change the location it loads from, pass the `--basedir` option.

.. code-block:: shell-session

    python ocdskingfisher-cli status --basedir /data ...
