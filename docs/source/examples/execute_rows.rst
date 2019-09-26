.. _examples_fetch_rows_with_geometry:

Fetching Rows With Geometry
===========================

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
