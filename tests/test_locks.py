#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from psycopg2.sql import SQL
from normanpg.functions import schema_exists, table_exists
from normanpg.locks import lock_table, is_locked
from normanpg.pg import connect, execute
from normanpg.schemas import TempSchema


def test_is_locked(tmp_db):
    """
    Arrange: Create a temporary schema and a test table.
    Act:  Lock the test table within a connection and close the connection.
    Assert: The table is locked only when expected.

    :param tmp_db: the temporary testing database
    """
    # Create a schema in which to perform the test.
    with TempSchema(tmp_db.dburl) as temp_schema:
        # Create a test table.
        test_table_name = 'test_is_locked_table'
        execute(
            cnx=tmp_db.dburl,
            query=(
                f"CREATE TABLE {temp_schema.schema_name}.{test_table_name}("
                f"id serial PRIMARY KEY"
                f");"
            )
        )
        # Make sure the table exists.
        assert table_exists(
            cnx=tmp_db.dburl,
            table_name=test_table_name,
            schema_name=temp_schema.schema_name
        ), "The test table should have been created."
        # The test table shouldn't be locked at this point.
        assert not is_locked(
            cnx=tmp_db.dburl,
            table_name=test_table_name,
            schema_name=temp_schema.schema_name
        ), "The test table should not be locked after creation."
        # Start a new connection.
        with connect(url=tmp_db.dburl) as cnx:
            # Lock the table.
            lock_table(
                cnx=cnx,
                table_name=test_table_name,
                schema_name=temp_schema.schema_name
            )
            # As long as the connection is open, the table should be locked.
            # (Notice we test it from a separate connection.)
            assert is_locked(
                cnx=tmp_db.dburl,
                table_name=test_table_name,
                schema_name=temp_schema.schema_name
            ), (
                "The table should be locked as long as the connection "
                "is open."
            )
        # The table should not be locked after the connection is closed.
        assert not is_locked(
            cnx=tmp_db.dburl,
            table_name=test_table_name,
            schema_name=temp_schema.schema_name
        ), (
            "The table should be unlocked after the connection that locked "
            "it is closed."
        )
