#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 11/30/19
"""
This module contains conveniences for working with database schemas.

.. currentmodule:: normanpg.schemas
.. moduleauthor:: Pat Daburu <pat@daburu.net>
"""
import random
import string
from .functions import create_schema, drop_schema


def temp_name(rand: int = 8, prefix: str = None):
    """
    Generate a randomized of a specified length and an optional prefix.

    :param rand: the number of random characters in the name
    :param prefix: the prefix
    :return: the randomized name
    """
    # Negative numbers don't make sense in this context.
    if rand < 0:
        raise ValueError("The random factor may not be less than zero (0).")
    # We would like some sane amount of information from which to format a
    # name.
    if rand < 3:
        if prefix and prefix.strip():
            return prefix
        else:
            raise ValueError(
                "The name must include a random factor of at least three (3) "
                "characters or a prefix."
            )
    # Construct the randomized part of the string.
    chars = ''.join(random.choice(string.ascii_lowercase) for i in range(rand))
    # Based on whether or not there is a prefix, construct and return a new
    # name.
    return (
        f"{prefix}_{chars}"
        if prefix
        else chars
    ).strip()


class TempSchema:
    """Context manager that creates a temporary schema."""

    def __init__(
            self,
            url: str,
            rand: int = 8,
            prefix: str = None
    ):
        """
        Context manager that creates a temporary schema.

        :param url: the database URL
        :param rand: the number of random characters to place in the name
        :param prefix: the name prefix
        """
        self._url = url
        self._prefix = prefix
        # Note to the future: Make sure the names don't clash.
        self._schema_name = temp_name(rand=rand, prefix=prefix)

    @property
    def url(self) -> str:
        """Get the database URL."""
        return self._url

    @property
    def prefix(self) -> str:
        """Get the prefix."""
        return self._prefix

    @property
    def schema_name(self) -> str:
        """Get the schema name."""
        return self._schema_name

    def __enter__(self):
        """Enter the context."""
        create_schema(url=self.url, schema=self._schema_name)
        return self

    def __exit__(self, type_, value, traceback):
        """Exit the context."""
        drop_schema(url=self.url, schema=self._schema_name)
