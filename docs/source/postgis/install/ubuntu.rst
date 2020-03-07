.. _install_postgis_ubuntu:

Installing PostgreSQL and PostGIS on Ubuntu
===========================================

# TODO: Reference THIS...
https://kitcharoenp.github.io/postgresql/postgis/2018/05/28/set_up_postgreSQL_postgis.html

You can use the UbuntuGIS.



Add the Repository
------------------

We'll start by adding the `UbuntuGIS <https://wiki.ubuntu.com/UbuntuGIS>`_
repository.

Verify Your Ubuntu Version
^^^^^^^^^^^^^^^^^^^^^^^^^^

In this example we're using
`Ubuntu 18.04 LTS <http://releases.ubuntu.com/18.04/>`_, but if you're
using another version you may need the release codename.  You can get it
using ``lsb_release``.

.. code-block:: sh

    $ sudo lsb_release -a

.. code-block:: coq
    :emphasize-lines: 5

    No LSB modules are available.
    Distributor ID:	Ubuntu
    Description:	Ubuntu 18.04 LTS
    Release:	18.04
    Codename:	bionic

Add the Repository to ``sources.list``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this example, the release code name is *"bionic"*.  If you're using another
release, replace *bionic* with the release code name.

.. code-block::

    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bionic-pgdg main" >> /etc/apt/sources.list'


Add the Keys
^^^^^^^^^^^^

Use ``apt-keys`` to add the key used by apt to authenticate packages from the
repository.

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
