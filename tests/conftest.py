#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import NamedTuple
import testing.postgresql
import pytest


class TmpDb(NamedTuple):
    """Temporary testing database details."""
    pgdb: testing.postgresql.Postgresql  #: testing db object
    dburl: str  #: the database URL


@pytest.yield_fixture(scope='session', name='tmp_db')
def tmp_db():
    """
    Generates a temporal database using the testing.postgresql package
    """

    # Initialize the temporary PostgreSQL instance.
    pgdb = testing.postgresql.Postgresql()

    # Get URL and other derived data.
    dburl = pgdb.url()

    yield TmpDb(
        pgdb=pgdb,
        dburl=dburl
    )

    # Shut down the temporary PostgreSQL instance and clean up the temporary
    # working directory.
    pgdb.stop()
