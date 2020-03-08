#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from psycopg2.sql import SQL
from normanpg.functions import schema_exists, table_exists
from normanpg.locks import lock_table, is_locked
from normanpg.pg import connect, execute
from normanpg.schemas import TempSchema


def test_is_locked(tmp_db):

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
        assert table_exists(
            cnx=tmp_db.dburl,
            table_name=test_table_name,
            schema_name=temp_schema.schema_name
        )
        assert not is_locked(
            cnx=tmp_db.dburl,
            table_name=test_table_name,
            schema_name=temp_schema.schema_name
        )
        with connect(url=tmp_db.dburl) as cnx:
            lock_table(
                cnx=cnx,
                table_name=test_table_name,
                schema_name=temp_schema.schema_name
            )
            assert is_locked(
                cnx=tmp_db.dburl,
                table_name=test_table_name,
                schema_name=temp_schema.schema_name
            )
        # The table should not be locked after the connection is closed.
        assert not is_locked(
            cnx=tmp_db.dburl,
            table_name=test_table_name,
            schema_name=temp_schema.schema_name
        )


    #     # Make note of the name so we may check after the block exists to
    #     # make sure it's gone.
    #     temp_schema_name = temp_schema.schema_name
    #     # Assert...
    #     assert schema_exists(
    #         cnx=tmp_db.dburl,
    #         schema=temp_schema.schema_name
    #     ), (
    #         "The temporary schema should exist within the 'with' block."
    #     )
    # # Assert...
    # assert temp_schema_name is not None, (
    #     "A temporary schema name should be generated."
    # )
    # assert not schema_exists(
    #     cnx=tmp_db.dburl,
    #     schema=temp_schema.schema_name
    # ), "The temporary schema should not exist after the 'with' block exits."
