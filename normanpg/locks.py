#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 3/8/20
"""
Lock tables and rows (if you must).

.. currentmodule:: normanpg.locks
.. moduleauthor:: Pat Daburu <pat@daburu.net>
"""
from enum import Enum
from typing import Iterable, NamedTuple, Union
from phrasebook import SqlPhrasebook
from psycopg2.sql import SQL, Literal
import psycopg2.extensions
from .errors import NormanPgException
from .pg import compose_table, execute, execute_rows


_PHRASEBOOK = SqlPhrasebook().load()  #: the module phrasebook


class NormanPgLockException(NormanPgException):
    """Raised upon explicit locking errors."""


class LockModes(Enum):
    """PostgreSQL lock modes."""
    ACCESS_EXCLUSIVE = 'ACCESS EXCLUSIVE'


class LockInfo(NamedTuple):
    """Table lock information."""
    table: str  #: the name of the table
    schema: str  #: the schema in which the table resides
    pid: int  #: the ID of the process that holds the lock


def lock_table(
        cnx: Union[str, psycopg2.extensions.connection],
        table_name: str,
        schema_name: str = None,
        mode: LockModes = LockModes.ACCESS_EXCLUSIVE,
        nowait: bool = False
):
    """

    :param cnx: a connection string or open database connection
    :param table_name: the table name
    :param schema_name: the schema name
    :param mode: the locking mode
    :param nowait: `True` to fail immediately if the lock conflicts with
        an existing lock
    """
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('lock_table')).format(
        table=compose_table(table_name=table_name, schema_name=schema_name),
        mode=SQL(mode.value),
        nowait=SQL('NOWAIT' if nowait else '')
    )
    # Execute it!
    execute(cnx=cnx, query=query)


def lock_info(
    cnx: Union[str, psycopg2.extensions.connection],
    table_name: str,
    schema_name: str,
) -> Iterable[LockInfo]:
    """
    Get lock information for a table.

    :param cnx: a connection string or open database connection
    :param table_name:
    :param schema_name:
    :return:
    """
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('lock_info')).format(
        table=Literal(table_name),
        schema=Literal(schema_name)
    )
    # Go get 'em!
    for row in execute_rows(cnx=cnx, query=query):
        yield LockInfo(
            table=table_name,
            schema=schema_name,
            pid=row['pid']
        )


def is_locked(
    cnx: Union[str, psycopg2.extensions.connection],
    table_name: str,
    schema_name: str,
) -> bool:
    """
    Does that table have locks on it?

    :param cnx: a connection string or open database connection
    :param table_name: the name of the table
    :param schema_name: the name schema in which the table resides
    :return:  ``True`` if and only if there are locks on the table
    """
    # Get information about any locks on the table.
    lock_infos = list(lock_info(
        cnx=cnx,
        table_name=table_name,
        schema_name=schema_name
    ))
    # If there is information about locks...
    if lock_infos:
        # ...in the simplest terms, the table is "locked" in some way.
        return True
    # There is no lock information, so the table isn't locked.
    return False
