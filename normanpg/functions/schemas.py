#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 11/30/19
"""
This module contains database schema functions.

.. currentmodule:: normanpg.schemas
.. moduleauthor:: Pat Daburu <pat@daburu.net>
"""
from typing import Union
from phrasebook import SqlPhrasebook
import psycopg2.extensions
from psycopg2.sql import Literal, SQL
from ..errors import NormanPgException
from ..pg import (
    execute, execute_scalar,
)

_PHRASEBOOK = SqlPhrasebook().load()


def create_schema(
        cnx: Union[str, psycopg2.extensions.connection],
        schema: str,
):
    """
    Create a schema in the database.

    :param cnx: a connection string or open database connection
    :param schema: the name of the schema
    """
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('create_schema')).format(
        schema=SQL(schema)
    )
    # Execute it!
    execute(cnx=cnx, query=query)


def drop_schema(
        cnx: Union[str, psycopg2.extensions.connection],
        schema: str,
        cascade: bool = True
):
    """
    Drop a schema in the database.

    :param cnx: a connection string or open database connection
    :param schema: the name of the schema
    :param cascade: ``True`` to drop the schema even if it is not empty,
        otherwise the attempt fails
    """
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('drop_schema')).format(
        schema=SQL(schema),
        cascade=SQL('CASCADE' if cascade else 'RESTRICT')
    )
    # Execute it!
    execute(cnx=cnx, query=query)


def schema_exists(
        cnx: Union[str, psycopg2.extensions.connection],
        schema: str = None
) -> bool:
    """
    Does a given schema exist within a database?

    :param cnx: a connection string or open database connection
    :param schema: the name of the database to test
    :return: `True` if the schema exists, otherwise `False`
    """

    # Prepare the query.
    query = SQL(_PHRASEBOOK.gets('schema_exists')).format(
        schema=Literal(schema)
    )
    # The query should return a count of the appearances of the schema.
    count = execute_scalar(cnx=cnx, query=query, cast=int)

    # If the count is more than 1, there is something wrong with the result
    # (since it should be the number of databases with the given name).
    if count > 1:
        raise NormanPgException(
            f'The database returned an unexpected result: {count}'
        )
    # If the name appeared exactly one (1) time, the database exists.
    # Otherwise, it doesn't.
    return count == 1
