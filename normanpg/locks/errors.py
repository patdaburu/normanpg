#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 3/8/20
"""
Things can go wrong with explicit locks.

.. currentmodule:: normanpg.locks.errors
.. moduleauthor:: Pat Daburu <pat@daburu.net>
"""
from ..errors import NormanPgException


class NormanPgLockException(NormanPgException):
    """Raised upon explicit locking errors."""
