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
from psycopg2.sql import SQL, Identifier
import psycopg2.extensions
from .errors import NormanPgException
from .pg import compose_table, execute, execute_rows


_PHRASEBOOK = SqlPhrasebook().load()  #: the module phrasebook


class NormanPgLockException(NormanPgException):
    """Raised upon explicit locking errors."""


class LockModes(Enum):
    """PostgreSQL lock modes."""
    ACCESS_EXCLUSIVE = 'ACCESS_EXCLUSIVE'


class LockInfo(NamedTuple):
    table: str
    schema: str
    pid: int


def lock_table(
        cnx: Union[str, psycopg2.extensions.connection],
        table: str,
        schema: str = None,
        mode: LockModes = LockModes.ACCESS_EXCLUSIVE,
        nowait: bool = False
):
    """

    :param cnx: a connection string or open database connection
    :param table: the table name
    :param schema: the schema name
    :param mode: the locking mode
    :param nowait: `True` to fail immediately if the lock conflicts with
        an existing lock
    """
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('lock_table')).format(
        table=compose_table(table_name=table, schema_name=schema),
        mode=mode.value,
        nowait=SQL('NOWAIT' if nowait else '')
    )
    # Execute it!
    execute(cnx=cnx, query=query)


def lock_info(
    cnx: Union[str, psycopg2.extensions.connection],
    table: str,
    schema: str = None
) -> Iterable[LockInfo]:
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('lock_info')).format(
        table=Identifier(table),
        schema=Identifier(schema)
    )
    # Go get 'em!
    for row in execute_rows(cnx=cnx, query=query):
        yield LockInfo(
            table=table,
            schema=schema,
            pid=row['pid']
        )


def is_locked(
    cnx: Union[str, psycopg2.extensions.connection],
    table: str,
    schema: str = None
) -> bool:
    # Get information about any locks on the table.
    lock_infos = list(lock_info(
        cnx=cnx,
        table=table,
        schema=schema
    ))
    # If there is information about locks...
    if lock_infos:
        # ...in the simplest terms, the table is "locked" in some way.
        return True
    # There is no lock information, so the table isn't locked.
    return False
