#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPython integration and notebook utilities.

Provides functions for detecting IPython environments, managing variable
assignments in notebooks, and other IPython-specific functionality.
"""

import re
import builtins
from types import ModuleType
from typing import Any

import IPython
from IPython import get_ipython

from .logging import log

ipython_print_on_assignments: bool = (
    True  # Whether to print output from variable assignments in IPython terminal.
)
ipython_print_on_assignments_in_cells: bool = (
    False  # Whether to print output from variable assignments in IPython cells.
)
_ipython_binder_name: str = (
    '_ipython_binder'  # Name of IPython binder dictionary to put in builtins.
)
_ipython_binder: dict[str, Any] = None  # IPython binder dictionary.


def is_notebook() -> bool:
    """
    Check whether script is executed in IPython notebook.

    Returns:
        True if running in Jupyter notebook, False otherwise
    """
    ipython = get_ipython()
    if hasattr(ipython, '__class__') and hasattr(ipython.__class__, '__name__'):
        shell = ipython.__class__.__name__
        if shell == 'ZMQInteractiveShell':  # Jupyter notebook or qtconsole.
            return True
        elif shell == 'TerminalInteractiveShell':  # Terminal running IPython.
            return False
        else:  # Other IPython?
            return False
    else:  # Standard Python interpreter.
        return False


def ipython_nb_header() -> None:
    """
    Header to configure IPython.

    Sets up autoreload and patches for IPython notebook environment.
    """
    if not is_notebook():
        return

    # Configure IPython.
    ipython = get_ipython()
    ipython.run_line_magic('reload_ext', 'autoreload')
    ipython.run_line_magic('autoreload', '2')
    _patch_autoreloader()
    _patch_interactive_shell()

    log('IPython notebook header loaded.\n')


def ipython_bind_globals(glob: dict[str, Any]) -> None:
    """
    Bind global variables to IPython session.

    Global variables in module are persistent even when autoreloading with IPython.

    Args:
        glob: Global variables dictionary (typically globals())
    """
    if not is_notebook():
        return

    global _ipython_binder

    pac_name = glob['__name__']
    if pac_name not in _ipython_binder:
        _ipython_binder[pac_name] = {}
    _ipython_binder[pac_name]['globals'] = glob

    for pac_name, pac_bind in _ipython_binder.items():
        for glob_var_name, glob_var_val in pac_bind['globals'].items():
            if (
                not glob_var_name.startswith('__')
                and not glob_var_name.endswith('__')
                and not callable(glob_var_val)
                and not isinstance(glob_var_val, ModuleType)
            ):
                if glob_var_name not in pac_bind:
                    pac_bind[glob_var_name] = {
                        'declared': glob_var_val,
                        'current': glob_var_val,
                    }


def _patch_autoreloader() -> None:
    """
    Patch autoreloader in IPython so that global variables are kept on autoreload.
    """
    global _ipython_binder_name, _ipython_binder

    def pre_loader() -> None:
        """Trigger on pre_cell_run before autoreloading module."""
        global _ipython_binder
        for pac_name, pac_bind in _ipython_binder.items():
            for glob_var_name, glob_var_val in pac_bind['globals'].items():
                if (
                    not glob_var_name.startswith('__')
                    and not glob_var_name.endswith('__')
                    and not callable(glob_var_val)
                    and not isinstance(glob_var_val, ModuleType)
                ):
                    if glob_var_name not in pac_bind:
                        pac_bind[glob_var_name] = {
                            'declared': glob_var_val,
                            'current': glob_var_val,
                        }
                    else:
                        pac_bind[glob_var_name]['current'] = glob_var_val

    def post_loader() -> None:
        """Trigger on pre_cell_run after autoreloading module."""
        global _ipython_binder
        for pac_name, pac_bind in _ipython_binder.items():
            for bind_var_name, bind_var in pac_bind.items():
                if not bind_var_name == 'globals':
                    current_val = bind_var['current']
                    prev_definition = bind_var['declared']
                    new_definition = pac_bind['globals'][bind_var_name]

                    if prev_definition != new_definition:
                        bind_var['declared'] = new_definition
                    elif prev_definition != current_val:
                        pac_bind['globals'][bind_var_name] = current_val

    if IPython.extensions.autoreload.superreload.__name__ == 'superreload':
        orig_superreload = IPython.extensions.autoreload.superreload

        def patched_superreload(*args: Any, **kw: Any) -> Any:
            """Keep global variable states upon module reload."""
            pre_loader()
            orig_superreload(*args, **kw)
            post_loader()

        IPython.extensions.autoreload.superreload = patched_superreload


def _patch_interactive_shell() -> None:
    """
    Patch InteractiveShell in IPython so that variables are printed on assignments in the chosen situations.
    """
    if IPython.InteractiveShell.run_ast_nodes.__name__ == 'run_ast_nodes':
        orig_run_ast_nodes = IPython.InteractiveShell.run_ast_nodes

        def patched_run_ast_nodes(*args: Any, **kw: Any) -> Any:
            """Print variable output on variable assignment."""
            if (
                'result' in kw
                and hasattr(kw['result'], 'info')
                and hasattr(kw['result'].info, 'raw_cell')
            ):
                raw_cell_text = re.sub(' ', '', kw['result'].info.raw_cell)
                if ipython_print_on_assignments:
                    if not raw_cell_text.startswith('#%%'):
                        kw['interactivity'] = 'last_expr_or_assign'
                    elif ipython_print_on_assignments_in_cells:
                        kw['interactivity'] = 'last_expr_or_assign'
            return orig_run_ast_nodes(*args, **kw)

        IPython.InteractiveShell.run_ast_nodes = patched_run_ast_nodes


def _setup_ipython_binding() -> None:
    """
    Setup IPython global variable binding.
    """
    global _ipython_binder_name, _ipython_binder

    if _ipython_binder_name not in builtins.__dict__:
        builtins.__dict__[_ipython_binder_name] = {}
    _ipython_binder = builtins.__dict__[_ipython_binder_name]


_setup_ipython_binding()
ipython_bind_globals(globals())
