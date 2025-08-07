#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging utilities and file logging management.

Provides logging functionality with support for file output, multiple
log categories, and configurable logging behavior.
"""

import os
from pathlib import Path
from typing import Any, Callable, Union

from .printing_utils import prepend_string_lines
from .timer_utils import get_local_datetime


log_file_folder: str = None  # Log file folder.
log_file_name_dic: dict[str, str] = (
    None  # Dictionary of log file names for each log category.
)
append_to_log_files: bool = (
    False  # Append to existing log files instead of overwriting.
)
_log_file_has_started: bool = (
    False  # Keep track of whether writing to log file has started.
)

# Log controller.
loggers: dict[str, dict[str, Union[bool, Callable]]] = {
    'local_file': {
        'active': False,  # Default=False.
        'err': lambda message: _log_file_write(
            log_file_name_dic['err'],
            prepend_string_lines(get_local_datetime() + ': Error: ', message),
        ),
        'inf': lambda message='': _log_file_write(
            log_file_name_dic['inf'],
            prepend_string_lines(get_local_datetime() + ': ', message),
        ),
    },
    'local_print': {
        'active': True,  # Default=True.
        'err': lambda message: print(f'Error: {message}'),
        'inf': lambda message='': print(f'{message}'),
    },
}


def log(*args: Any, str_func: Callable[[Any], str] = lambda item: str(item)) -> None:
    """
    Log string with given log priority.

    Args:
        *args: Variable arguments - can be:
               - No args: logs empty info message
               - 1 arg: logs the argument as info
               - 2 args: first is priority ('inf' or 'err'), second is the item to log
        str_func: Function to convert items to strings

    Raises:
        Exception: If more than 2 arguments are provided
    """
    if len(args) == 0:
        priority = 'inf'
        item = None
    elif len(args) == 1:
        priority = 'inf'
        item = args[0]
    elif len(args) == 2:
        priority = args[0]
        item = args[1]
    else:
        raise Exception(
            f'Function <log> takes 0-2 argument, but {len(args)} arguments were given.'
        )

    for logger in loggers:
        if priority in loggers[logger] and loggers[logger]['active']:
            if item is None:
                loggers[logger][priority]()
            else:
                loggers[logger][priority](str_func(item))


def log_dic_lines(*args: Any) -> None:
    """
    Log dictionary with each key, value on a new line.

    Args:
        *args: Arguments passed to log function, where dictionary should be the last argument
    """
    str_func = lambda dic: '\n'.join(f'{key}: {value}' for key, value in dic.items())
    log(*args, str_func=str_func)


def setup_file_logging(
    log_folder_path: str,
    log_file_names: Union[str, dict[str, str]],
    append_to_existing: bool = False,
    enable_local_file_logging: bool = True,
) -> None:
    """
    Initialize file logging with the specified parameters.

    Args:
        log_folder_path: Path to the folder where log files will be stored
        log_file_names: Dictionary mapping log priorities to filenames
                       (e.g., {'err': 'error.log', 'inf': 'info.log'})
                       or a single filename string for all priorities
        append_to_existing: Whether to append to existing log files or overwrite them
        enable_local_file_logging: Whether to enable local file logging
    """
    global log_file_folder, log_file_name_dic, append_to_log_files

    log_file_folder = log_folder_path

    if isinstance(log_file_names, dict):
        log_file_name_dic = log_file_names.copy()
    else:
        log_file_name_dic = {'err': log_file_names, 'inf': log_file_names}

    append_to_log_files = append_to_existing
    loggers['local_file']['active'] = enable_local_file_logging

    info_filename = log_file_name_dic.get('inf', list(log_file_name_dic.values())[0])
    log(f'Logging enabled to log file: <{log_file_folder}/{info_filename}>.')


def _log_file_write(log_file_name: str, string: str) -> None:
    """
    Log file writer.

    Args:
        log_file_name: Name of the log file to write to
        string: String content to write to the log file

    Raises:
        Exception: If log file folder or names are not set
    """
    from .io import make_folders

    global _log_file_has_started, log_file_name_dic

    if log_file_folder is None:
        raise Exception('Logging to file enabled, but log file folder not set.')
    if log_file_name_dic is None:
        raise Exception('Logging to file enabled, but log file names not set.')

    log_file_path = os.path.join(log_file_folder, log_file_name)

    if not _log_file_has_started:
        # Make folder(s) if necessary
        if not Path(log_file_folder).is_dir():
            activated = loggers['local_file']['active']
            loggers['local_file']['active'] = False
            make_folders([log_file_folder], print_nl=False)
            loggers['local_file']['active'] = activated

        if append_to_log_files:
            with open(log_file_path, 'a') as out_file:
                print(string, file=out_file)
        else:
            with open(log_file_path, 'w') as out_file:
                print(string, file=out_file)

        _log_file_has_started = True

    else:
        with open(log_file_path, 'a') as out_file:
            print(string, file=out_file)
