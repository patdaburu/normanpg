#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 9/29/19
"""
.. currentmodule:: normanpg.functions
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Within this package are handy functions.
"""
from .db_info import create_db, db_exists, parse_dbname, touch_db
from .table_info import geometry_column, srid, table_exists
