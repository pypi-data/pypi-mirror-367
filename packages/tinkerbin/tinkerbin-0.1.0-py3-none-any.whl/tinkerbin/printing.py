#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Printing and output formatting utilities.

Provides functions for formatted output including headers, system information
display, and other printing utilities for enhanced console output.
"""

import sys
import platform
import psutil
import re
import math
from datetime import datetime

from .logging import log
from .utils import get_script_name


def print_header(string: str) -> None:
    """
    Print formatted header with content string.

    Creates a header with equals signs padding around the string.

    Args:
        string: Text to display in the header
    """
    width = 31
    pad1 = max(int(math.floor((width - (len(string) + 3)) / 2.0)), 4)
    pad2 = max(width - (pad1 + len(string) + 3), 4)
    log('=' * pad1 + ' ' + string + ': ' + '=' * pad2)


def print_sys_info() -> None:
    """
    Print info about system and python environment.

    Displays comprehensive system information including:
    - Platform and OS details
    - Hardware specifications (CPU, RAM)
    - Python version
    - Current time and script name
    """
    print_header('System information')
    log('Platform: ' + platform.platform())
    log('OS Version: ' + platform.version())
    log('Machine: ' + platform.machine())
    log(
        'Number of CPUs: '
        + str(psutil.cpu_count())
        + ' ('
        + str(psutil.cpu_count(logical=False))
        + ' physical)'
    )
    log('RAM: ' + str(round(psutil.virtual_memory().total / (1024.0**3))) + ' GB')
    log('Python version: ' + re.sub('\n', '', sys.version))
    time_format = '%Y-%m-%d %H:%M:%S UTC%z(%Z)'
    log('Time: ' + datetime.now().astimezone().strftime(time_format))
    log('Script: ' + get_script_name(suffix=True))
    log()
