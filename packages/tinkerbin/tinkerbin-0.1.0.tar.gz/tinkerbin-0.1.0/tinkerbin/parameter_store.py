#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter storage and management utilities.

Provides functionality for tracking and managing parameter declarations,
storing parameter values, and handling parameter state in scripts.
"""

from typing import Any, Optional

from .logging import log
from .ipython import is_notebook
from .printing import print_header

_before_parameter_names: Optional[list[str]] = (
    None  # All variables in scope before parameter declarations.
)
_declared_parameters: Optional[dict[str, Any]] = (
    None  # All variables declared since <set_before_vars()> was called.
)
_lock_parameter_vars: bool = (
    False  # Lock parameter saving variables, useful for IPython scripts.
)


def set_before_vars(glob: dict[str, Any]) -> None:
    """
    Set list of global variables before parameter definitions.

    Args:
        glob: Global variables dictionary (typically globals())
    """
    global _before_parameter_names
    if not _lock_parameter_vars:
        _before_parameter_names = list(glob.keys())


def add_after_vars(glob: dict[str, Any]) -> None:
    """
    Add global variables after parameters definitions.

    Args:
        glob: Global variables dictionary (typically globals())

    Raises:
        Exception: If set_before_vars was not called first
    """
    global _declared_parameters

    if _before_parameter_names is None:
        raise Exception('Attempted to set after vars, but before vars were not set.')

    if _declared_parameters is None:
        _declared_parameters = {}

    # Get all globally defined variables.
    if not _lock_parameter_vars:
        declared_var_names = [
            var_name
            for var_name in glob.keys()
            if var_name not in _before_parameter_names + ['_before_var_names']
        ]
        for var_name in declared_var_names:
            _declared_parameters[var_name] = glob[var_name]
    else:
        for var_name in _declared_parameters:
            _declared_parameters[var_name] = glob[var_name]


def print_defined_vars() -> None:
    """
    Print all defined parameters.

    If running in IPython notebook, locks parameter saving variables so that
    rerunning the code prints the same parameters.

    Raises:
        Exception: If add_after_vars was not called first
    """
    global _declared_parameters, _lock_parameter_vars

    if _declared_parameters is None:
        raise Exception(
            'Attempted to print defined variables, but after vars were not set.'
        )

    # If IPython notebook, lock parameters saving variables so that rerunning the code prints the same.
    if is_notebook():
        _lock_parameter_vars = True

    # Print parameters.
    print_header('Parameters')
    log(
        '\n'.join(
            [
                var_name + ': ' + str(_declared_parameters[var_name])
                for var_name in _declared_parameters.keys()
            ]
        )
    )
