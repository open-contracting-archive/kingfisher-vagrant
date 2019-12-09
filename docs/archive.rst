The Archive Server
==================

Purpose
-------

The archive server stores old data files that have been downloaded by scrape.

It does this so that if we need to load old files for historical analysis later,
we can use the files on the archive server and do so by the local load function in process.

Installation on the Scrape and Process server
---------------------------------------------

Currently the script needs to be on one server that has both scrape and process parts.
(This is because it needs to directly access both the database and the source files)

The script is at https://github.com/open-contracting/kingfisher-archive

The user account that runs it needs

  *  ssh access to the archive server
  *  access to the database (a .pgpass file)
  *  sudo permission to delete files from the scrape account

More than one instance of the script should not run at once. This is because they may clash, and try and archive the same collection at the same time.

To ensure this, the script exits after it has found and archived one collection.

The script is started once per day by a cron job.

Output can be piped to a log file, for debugging purposes. On hosted Kingfisher, these are in /home/archive/logs/

Installation on the Archive server
----------------------------------

There is no software part to install on this side.

Simply make sure the archive account

  *  can be accessed over SSH
  *  has a /home/archive/data/ folder
