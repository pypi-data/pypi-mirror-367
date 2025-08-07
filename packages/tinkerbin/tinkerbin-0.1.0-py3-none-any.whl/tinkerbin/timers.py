#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timer functions for measuring execution time.

Provides functionality for starting timers, measuring elapsed time,
and printing timing information for performance monitoring.
"""

from datetime import datetime
from typing import Optional

from .logging import log

_start_time: Optional[datetime] = None  # Time the clock was started.


def start_timer() -> None:
    """
    Start the clock for timing.

    Records the current time as the start time for elapsed time calculations.
    """
    global _start_time
    _start_time = datetime.now()


def print_timing() -> None:
    """
    Prints the time elapsed since start_timer() was called.

    Raises:
        Exception: If start_timer() was not called first
    """
    global _start_time

    if _start_time is None:
        raise Exception('Attempted to find elapsed time, but start time was not set.')

    end_time = datetime.now()
    log(f'Elapsed time: {end_time - _start_time}.')


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
