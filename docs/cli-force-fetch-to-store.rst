Command line tool - force-fetch-to-store option
===============================================

This command takes a collection that is somehow stuck in the fetch stage and forces it to instantly move on to the store stage.

The next time you `run` this collection, it should start at the store stage with no problems.

Note this forcing process is irreversible - once done, it can not be undone.

.. code-block:: shell-session

    python ocdskingfisher-cli --verbose run australia_nsw
    ..... get bored, stop process .....
    python ocdskingfisher-cli force-fetch-to-store --run australia_nsw
    python ocdskingfisher-cli --verbose run australia_nsw

This might be needed:

  *  because there were errors in the fetch stage.
  *  because the fetch stage is just taking far to long, and we want to store the data we already have for analysis.


