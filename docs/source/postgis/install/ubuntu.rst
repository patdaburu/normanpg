.. _install_postgis_ubuntu:

Installing PostgreSQL and PostGIS on Ubuntu
===========================================

# TODO: Reference THIS...
https://kitcharoenp.github.io/postgresql/postgis/2018/05/28/set_up_postgreSQL_postgis.html

Add the Repository
------------------

sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bionic-pgdg main" >> /etc/apt/sources.list'


Add the Keys
------------

.. code-block:: sh

    wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
    sudo apt update


Install the Packages
--------------------

.. code-block:: sh

    sudo apt install postgresql-12
    sudo apt install postgresql-12-postgis-2.5
    sudo apt install postgresql-12-postgis-scripts

Change the Listener Port (Optional)
-----------------------------------

Historically PostgreSQL has listened on port *5432*.  When you install
PostgreSQL 12 it may default to listening on port *5433*.  If you want to
change the listener port you can edit
``/etc/postgresql/12/main/postgresql.conf`` and look for the ``port``
configuration option.

.. code-block:: ini

    port = 5433                             # (change requires restart)

After you make this change you'll need to restart the service for it to take
effect.

.. code-block::

    sudo service postgresql restart
