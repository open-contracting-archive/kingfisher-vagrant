Parallelism
===========

This explains what you can and can not parallelize in this tool.

On one collection, you should only run one operation at a time. The operations do not currently support parallelism.

For example, running ...

.. code-block:: shell-session

    python ocdskingfisher-cli run taiwan &
    python ocdskingfisher-cli run taiwan &

... will not mean the run is twice as fast - it will just break it!

On different collections, any operations can be performed at the same time, and the only limit is the capacity of your server.

For example, running ...

.. code-block:: shell-session

    python ocdskingfisher-cli run taiwan &
    python ocdskingfisher-cli run canada_buyandsell &

... is fine.
