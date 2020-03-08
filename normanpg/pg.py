#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 9/22/19 by Pat Blair
"""
This module contains the basic PostgreSQL functions.

.. currentmodule:: pg
.. moduleauthor:: Pat Blair <pblair@geo-comm.com>
"""
import inspect
import logging
import os
from typing import Any, Callable, Iterable, Union
from urllib.parse import urlparse, ParseResult
import psycopg2.extras
import psycopg2.sql
from psycopg2.sql import Identifier, SQL
import psycopg2.extensions
from .errors import NormanPgException


DEFAULT_ADMIN_DB = os.environ.get(
    'DEFAULT_ADMIN_DB',
    'postgres'
)  #: the default administrative database name
DEFAULT_PG_PORT: int = int(os.environ.get(
    'DEFAULT_PG_PORT',
    5432)
)  #: the default Postgres database port


class InvalidDbResult(NormanPgException):
    """Raised in response to an invalid result returned from the database."""


def log_query(
        crs: psycopg2.extensions.cursor,
        caller: str,
        query: str or psycopg2.sql.Composed
):
    """
    Log a SQL query.

    :param crs: the execution cursor
    :param caller: the caller
    :param query: the query
    """
    query_str = query if isinstance(query, str) else query.as_string(crs)
    logging.getLogger(__name__).debug(f'[{caller}] {query_str}')


def connect(
        url: str,
        dbname: str = None,
        autocommit: bool = False
) -> psycopg2.extensions.connection:
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


def execute_scalar(
        cnx: Union[str, psycopg2.extensions.connection],
        query: Union[str, psycopg2.sql.Composed],
        caller: str = None,
        cast: Callable[[Any], Any] = None
) -> Any or None:
    """
    Execute a query that returns a single, scalar result.

    :param cnx: an open psycopg2 connection or the database URL
    :param query: the `psycopg2` composed query
    :param caller: identifies the caller (for diagnostics)
    :param cast: a function to cast the value returned
    :return: the scalar string result (or `None` if the query returns no
        result)
    """
    # Get the name of the calling function so we can include it in the logging
    # statement.
    caller = caller if caller else inspect.stack()[1][3]
    # Make sure the query is `Composed`.
    _query = (
        psycopg2.sql.SQL(query).string
        if isinstance(query, str)
        else query
    )

    def _execute_scalar(
            ocnx: psycopg2.extensions.connection,
    ) -> Any:
        """
        Execute a query on an open cursor.

        :param ocnx: an open connection database connection
        :return: the first value in the first row returned by the query
        """
        with ocnx.cursor() as crs:
            # Log the query.
            log_query(crs=crs, caller=caller, query=_query)
            # Execute!
            try:
                crs.execute(_query)
            except SyntaxError:
                logging.exception(_query.as_string(crs))
                raise
            # Get the first column from the first result.
            return crs.fetchone()[0]

    # If the caller passed us a connection string...
    if isinstance(cnx, str):
        # ...get a connection and use the helper method to execute the query.
        with connect(url=cnx) as _cnx:
            return _execute_scalar(ocnx=_cnx)
    # It looks as though we were given an open connection, so execute the
    # query on it.
    value = _execute_scalar(ocnx=cnx)
    # If the value came back empty...
    if value is None:
        return None  # ...the caller gets an empty value.
    # If the caller gave us a casting function...
    if cast is not None:
        # ...cast the value and return it.
        return cast(value)
    # Otherwise, just return whatever we got.
    return value


def execute_rows(
        cnx: Union[str, psycopg2.extensions.connection],
        query: Union[str, psycopg2.sql.Composed],
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
    # Make sure the query is `Composed`.
    _query = (
        psycopg2.sql.SQL(query).string
        if isinstance(query, str)
        else query
    )

    def _execute_rows(
            ocnx: psycopg2.extensions.connection,
    ) -> Iterable[psycopg2.extras.DictRow]:
        """
        Execute ``_query`` on an open cursor.

        :param ocnx: an open database connection
        :return: an iteration of `DictRow` instances representing the rows
        """
        with ocnx.cursor(cursor_factory=psycopg2.extras.DictCursor) as crs:
            # Log the query.
            log_query(crs=crs, caller=caller, query=_query)
            # Execute!
            try:
                crs.execute(_query)
            except SyntaxError:
                logging.exception(_query.as_string(crs))
                raise
            # Fetch the rows and yield them to the caller.
            for _row in crs:
                yield _row

    # If the caller passed us a connection string...
    if isinstance(cnx, str):
        # ...get a connection and use the helper method to execute the query.
        with connect(url=cnx) as _cnx:
            for row in _execute_rows(ocnx=_cnx):
                yield row
    else:
        # It looks as though we were given an open connection, so execute the
        # query on it.
        for row in _execute_rows(ocnx=cnx):
            yield row


def execute(
        cnx: Union[str, psycopg2.extensions.connection],
        query: Union[str, psycopg2.sql.Composed],
        caller: str = None
):
    """
    Execute a query that returns no result.

    :param cnx: an open connection or database connection string
    :param query: the `psycopg2` composed query
    :param caller: identifies the caller (for diagnostics)

    .. seealso::

        * :py:func:`execute_scalar`
        * :py:func:`execute_rows`
    """
    # Get the name of the calling function so we can include it in the logging
    # statement.
    caller = caller if caller else inspect.stack()[1][3]
    # Make sure the query is `Composed`.
    _query = (
        psycopg2.sql.SQL(query).string
        if isinstance(query, str)
        else query
    )

    def _execute(
            ocnx: psycopg2.extensions.connection
    ):
        """
        Execute a query on an open cursor.

        :param ocnx: an open connection or database connection string
        """
        with ocnx.cursor() as crs:
            # Log the query.
            log_query(crs=crs, caller=caller, query=_query)
            # Execute!
            try:
                crs.execute(_query)
            except SyntaxError:
                logging.exception(query.as_string(_query))
                raise

    # If the caller passed us a connection string...
    if isinstance(cnx, str):
        # ...get a connection and use the helper method to execute the query.
        with connect(url=cnx) as _cnx:
            _execute(ocnx=_cnx)
    else:
        # It looks as though we were given an open connection, so execute the
        # query on it.
        _execute(ocnx=cnx)


def compose_table(
        table_name: str,
        schema_name: str = None
) -> psycopg2.sql.Composed:
    """
    Get a composed SQL object for a fully-qualified table name.

    :param table_name: the table name
    :param schema_name: the schema name
    :return: a composed SQL object
    """
    if schema_name is not None:
        return psycopg2.sql.SQL('{}.{}').format(
            Identifier(schema_name),
            Identifier(table_name)
        )
    return SQL('{}').format(SQL(table_name))
