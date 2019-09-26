.. _examples_shared_connection:

Multiple Queries on a Single Connection
=======================================

Sometimes you need to execute multiple statements on a single connection.  Why?
Who knows?  Maybe you're creating a temporary table.  Or maybe you need to
execute multiple statements within a transaction.  Whatever the reason, we've
got you covered.

.. code-block:: python

    from normanpg import connect, execute, execute_rows

    # Where's the database?
    url = 'postgresql://postgres:postgres@localhost/postgis_cookbook'

    # Let's prepare a query to INSERT some data into a table.
    query1 = "INSERT INTO test(id, text) VALUES (1, 'hello')"

    # Then we'll turn around and query the table.
    query2 = "SELECT id, text FROM test WHERE id=1"

    # Open a new connection as a context manager.
    with connect(url) as cnx:

        # Execute the first query.
        execute(cnx=cnx, query=query1)

        # Now execute the second query on the same connection.
        for row in execute_rows(cnx=cnx, query=query2):
            print(f"id={row['id']}, text={row['text']}")


.. code-block:: coq

    id=1, text=hello
