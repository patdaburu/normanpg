#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 9/22/19 by Pat Blair
"""
.. currentmodule:: pg
.. moduleauthor:: Pat Blair <pblair@geo-comm.com>

This module needs a description.
"""
from datetime import datetime
import inspect
import logging
from typing import Any, Iterable, List, Generator, Union, Set, Tuple
from urllib.parse import urlparse, ParseResult
from functools import lru_cache
import psycopg2.extras
import psycopg2.sql
import psycopg2.extensions
from .errors import NormanPgException

__logger__ = logging.getLogger(__name__)  #: the module logger

DEFAULT_PG_PORT: int = 5432  #: the default Postgres database port


def connect(
        url: str,
        dbname: str = None,
        autocommit: bool = False
):
    """
    Get a connection to a Postgres database instance.

    :param url: the instance URL
    :param dbname: the target database name
    :param autocommit: Set the `autocommit` flag on the connection?
    :return: a psycopg2 connection

    .. note::

        If the caller does not provide the `dbname` parameter the function
        creates a connection to the database specified in the URL.
    """
    # Parse the URL.  (We'll need the pieces to construct a connection
    # string.)
    dbp: ParseResult = urlparse(url)
    # Create a dictionary to hold the arguments for the connection.  (We'll
    # unpack it later.)
    cnx_opt = {
        k: v for k, v in
        {
            'host': dbp.hostname,
            'port': int(dbp.port) if dbp.port is not None else DEFAULT_PG_PORT,
            'database': dbname if dbname is not None else dbp.path[1:],
            'user': dbp.username,
            'password': dbp.password
        }.items() if v is not None
    }
    cnx = psycopg2.connect(**cnx_opt)
    # If the caller requested that the 'autocommit' flag be set...
    if autocommit:
        # ...do that now.
        cnx.autocommit = True
    return cnx


def _execute_scalar(
    cnx,
    query: psycopg2.sql.Composed,
    caller: str
) -> Any:
    """
    This is a helper function for :py:func:`execute_scalar` that executes a
    query on an open cursor.

    :param cnx: an open connection or database connection string
    :param query: the query
    :param caller: identifies the call stack location
    """
    with cnx.cursor() as crs:
        # Log the query.
        __logger__.debug(f'[{caller}] {query.as_string(crs)}')
        # Execute!
        crs.execute(query)
        # Get the first column from the first result.
        return crs.fetchone()[0]


def execute_scalar(
        cnx,
        query: psycopg2.sql.Composed,
        caller: str = None
) -> Any or None:
    """
    Execute a query that returns a single, scalar result.

    :param cnx: an open psycopg2 connection or the database URL
    :param query: the `psycopg2` composed query
    :param caller: identifies the caller (for diagnostics)
    :return: the scalar string result (or `None` if the query returns no
        result)
    """
    # Get the name of the calling function so we can include it in the logging
    # statement.
    caller = caller if caller else inspect.stack()[1][3]
    # If the caller passed us a connection string...
    if isinstance(cnx, str):
        # ...get a connection and use the helper method to execute the query.
        with connect(url=cnx) as _cnx:
            return _execute_scalar(cnx=_cnx, query=query, caller=caller)
    # It looks as though we were given an open connection, so execute the
    # query on it.
    return _execute_scalar(cnx=cnx, query=query, caller=caller)


def _execute_rows(
    cnx,
    query: psycopg2.sql.Composed,
    caller: str
) -> Iterable[psycopg2.extras.DictRow]:
    """
    This is a helper function for :py:func:`execute_rows` that executes a
    query on an open cursor.

    :param cnx: an open connection or database connection string
    :param query: the query
    :param caller: identifies the call stack location
    :return: an iteration of `DictRow` instances representing the rows
    """
    with cnx.cursor() as crs:
        # Log the query.
        __logger__.debug(f'[{caller}] {query.as_string(crs)}')
        # Execute!
        crs.execute(query)
        # Fetch the rows and yield them to the caller.
        for row in crs:
            yield row


def execute_rows(
        cnx,
        query: psycopg2.sql.Composed,
        caller: str = None
) -> Iterable[psycopg2.extras.DictRow]:
    """
    Execute a query that returns an iteration of rows.

    :param cnx: an open connection or database connection string
    :param query: the `psycopg2` composed query
    :param caller: identifies the caller (for diagnostics)
    :return: an iteration of `DictRow` instances representing the row
    """
    # Get the name of the calling function so we can include it in the logging
    # statement.
    caller = caller if caller else inspect.stack()[1][3]
    # If the caller passed us a connection string...
    if isinstance(cnx, str):
        # ...get a connection and use the helper method to execute the query.
        with connect(url=cnx) as _cnx:
            for row in _execute_rows(cnx=_cnx, query=query, caller=caller):
                yield row
    # It looks as though we were given an open connection, so execute the
    # query on it.
    for row in _execute_rows(cnx=_cnx, query=query, caller=caller):
        yield row
