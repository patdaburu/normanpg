.. _examples_fetch_rows_with_geometry:

Fetching Rows With Geometry
===========================

In this example, we'll fetch some data from a table in the database using the
:py:func:`execute_rows <normanpg.pg.execute_rows>` function.  The table also
has a geometry (in a column called ``the_geom``).  We'll use the
:py:func:`shape <normanpg.geometry.shape>` function to convert the
`WKB <https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry#Well-known_binary>`_
returned by the database into a
`Shapely <https://shapely.readthedocs.io/en/stable/manual.html#points>`_ point
geometry.

.. note::

    Obviously, your data may vary.  The table we're pulling from in this example
    came from sample data referenced in the
    `PostGIS Cookbook <https://www.packtpub.com/application-development/postgis-cookbook-second-edition>`_.

.. code-block:: python

    from normanpg import execute_rows
    from normanpg.geometry import shape

    # Where's the database?
    url = 'postgresql://postgres:postgres@localhost/postgis_cookbook'

    # Let's prepare a SQL query.
    query = "SELECT place, the_geom FROM chp01.firenews"

    # Execute the query; iterate over the results.
    for row in execute_rows(cnx=url, query=query):

        # What's the value in the 'place' field?
        print(f"The place is called {row['place']}.")

        # Convert the WKB geometry into a Shapely geometry.
        point = shape(row['the_geom'])

        # Let's see what we got.
        print(f'The geometry is a {type(point)}.')

        # Now let's get some information from that point.
        print(f"The place's coordinates are {point.x}, {point.y}.")

.. code-block:: coq

    The place is called Μονοδέντρι.
    The geometry is a <class 'shapely.geometry.point.Point'>.
    The place's coordinates are 26.099052, 38.364272.

    ...
