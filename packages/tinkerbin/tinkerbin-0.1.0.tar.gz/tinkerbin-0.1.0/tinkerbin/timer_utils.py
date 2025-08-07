#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timer utility functions for datetime operations.

Provides functions for getting formatted datetime strings in different
timezones and other time-related utilities.
"""

from datetime import datetime


def get_local_datetime() -> str:
    """
    Get string with current date and time in local timezone.

    Returns:
        Formatted datetime string in local timezone with UTC offset
    """
    time_format = '%Y-%m-%d %H:%M:%S UTC%z(%Z)'
    string = datetime.now().astimezone().strftime(time_format)
    return string


def get_utc_datetime() -> str:
    """
    Get string with current date and time in UTC timezone.

    Returns:
        Formatted datetime string in UTC timezone
    """
    time_format = '%Y-%m-%d %H:%M:%S UTC'
    string = datetime.utcnow().strftime(time_format)
    return string
