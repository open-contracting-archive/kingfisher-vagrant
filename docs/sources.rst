Sources
=======

Remote Data
----------

The tool comes with sources - definitions of data you can download that already know
about all the API work that is needed to get the data.

A full list of remote sources is:

  *  armenia
  *  australia_nsw
  *  canada_buyandsell
  *  canada_montreal
  *  chile_compra
  *  colombia
  *  honduras_cost
  *  indonesia_bandung
  *  mexico_administracion_publica_federal
  *  mexico_cdmx
  *  mexico_grupo_aeroporto
  *  mexico_inai
  *  mexico_jalisco
  *  moldova
  *  paraguay_dncp
  *  paraguay_hacienda
  *  taiwan
  *  uganda
  *  uk_contracts_finder
  *  ukraine
  *  uruguay
  *  zambia

Local Data
----------

A special option exists to load a set of files from the disk into the database.

.. code-block:: shell-session

    python ocdskingfisher-cli --verbose run local_load --localloaddirectory /vagrant/georgiadata/ --localloaddatatype release_package

`localloaddirectory` should be the directory containing files.

`localloaddatatype` should be the type of files. Common types are:

  *  release
  *  record_package
  *  release_package

Sample mode will only process 5 files at random.

Limitations of this:

  *  A copy of the files will be made during the process - this may cause problems with disk space usage.
  *  Control codes will not be filtered out of these before trying to store them into the database.
  *  Only files directly in the directory will be included, files in sub-directories will not be included.
  *  All the files must be the same type - you can't mix different types in one load.
