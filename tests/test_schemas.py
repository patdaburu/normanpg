#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from normanpg.functions import schema_exists
from normanpg.schemas import TempSchema


def test_temp_schema(tmp_db):
    """
    Arrange/Act: Create a `TempSchema` in a `with` block.
    Assert: The temporary schema exists in the `with block` but not after.

    :param tmp_db: the temporary testing database
    """
    # We'll hang on to the temporary schema name.
    temp_schema_name: str or None = None
    with TempSchema(tmp_db.dburl) as temp_schema:
        # Make note of the name so we may check after the block exists to
        # make sure it's gone.
        temp_schema_name = temp_schema.schema_name
        # Assert...
        assert schema_exists(
            cnx=tmp_db.dburl,
            schema=temp_schema.schema_name
        ), (
            "The temporary schema should exist within the 'with' block."
        )
    # Assert...
    assert temp_schema_name is not None, (
        "A temporary schema name should be generated."
    )
    assert not schema_exists(
        cnx=tmp_db.dburl,
        schema=temp_schema.schema_name
    ), "The temporary schema should not exist after the 'with' block exits."
