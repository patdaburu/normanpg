#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 3/8/20
"""
Explicit locks for tables (if you must).

.. currentmodule:: normanpg.locks.tables
.. moduleauthor:: Pat Daburu <pat@daburu.net>
"""


def lock_table():
    pass


def unlock_table():
    pass

def is_locked() -> bool:
    pass


class TableLock:
    """Explicitly lock a table (if you must)."""
    pass

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()