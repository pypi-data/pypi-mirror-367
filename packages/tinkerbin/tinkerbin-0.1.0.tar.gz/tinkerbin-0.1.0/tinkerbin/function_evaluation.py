#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Function evaluation and inspection utilities.

Provides tools for function introspection, argument extraction,
and dynamic function evaluation with parameter handling.
"""

import inspect
import math
from typing import Any, Callable

import numpy


def get_func_args(func: Callable) -> list[str]:
    """
    Get list of function arguments.

    Args:
        func: Function to inspect

    Returns:
        List of argument names for the function
    """
    func_arg_dic = inspect.signature(func).parameters.items()
    func_args = [arg_name for arg_name, arg_spec in func_arg_dic]
    return func_args


def pass_only_args(func: Callable, arg_dic: dict[str, Any]) -> Any:
    """
    Pass items from arg_dic that are arguments to function as kwargs.

    Args:
        func: Function to call
        arg_dic: Dictionary of potential arguments

    Returns:
        Result of calling func with filtered arguments from arg_dic
    """
    func_args = get_func_args(func)
    pass_arg_dic = {}
    for arg_name in arg_dic:
        if arg_name in func_args:
            pass_arg_dic[arg_name] = arg_dic[arg_name]
    return func(**pass_arg_dic)


def eval_if_args_present(func: Callable, arg_dic: dict[str, Any]) -> Any:
    """
    Evaluate function if all its arguments are present in arg_dic and all argument values are valid.

    Valid argument values are not functions themselves, not None, and not NaN.

    Args:
        func: Function to potentially evaluate
        arg_dic: Dictionary of potential arguments

    Returns:
        Result of function evaluation if all arguments are present and valid,
        otherwise returns the unevaluated function
    """
    # Check needed arguments from function signature.
    func_args = get_func_args(func)

    # Build dictionary of arguments in arg_dic that are valid.
    value_arg_dic = {}
    for arg_name in arg_dic:
        arg_val = arg_dic[arg_name]
        if (
            not callable(arg_val)
            and arg_val is not None
            and not math.isnan(numpy.abs(arg_val))
        ):
            value_arg_dic[arg_name] = arg_dic[arg_name]

    # If all function arguments are present and values, evaluate function.
    if set(func_args) <= set(value_arg_dic):
        return pass_only_args(func, value_arg_dic)

    # Otherwise return unevaluated function back.
    else:
        return func


def eval_if_func(var: Any, arg_dic: dict[str, Any]) -> Any:
    """
    Evaluate eval_if_args_present of function if passed var is a function.

    Args:
        var: Variable that may or may not be a function
        arg_dic: Dictionary of potential arguments

    Returns:
        If var is callable, returns result of eval_if_args_present(var, arg_dic),
        otherwise returns var unchanged
    """
    if callable(var):
        return eval_if_args_present(var, arg_dic)
    else:
        return var


def arg_process(
    kw: dict[str, Any],
    arg_name: str,
    needed: bool,
    default_val_f: Callable[[dict[str, Any]], Any],
    prioritized_dic_list: list[dict[str, Any]] = None,
) -> None:
    """
    Process kwargs function argument.

    Args:
        kw: Dictionary to store processed argument in
        arg_name: Name of the argument to process
        needed: Whether the argument is required
        default_val_f: Function to generate default value if argument not found
        prioritized_dic_list: List of dictionaries to search for argument value in priority order

    Raises:
        Exception: If needed is True and argument is not found in any dictionary
    """
    if prioritized_dic_list is None:
        prioritized_dic_list = []

    found = False
    for i, dic in enumerate(prioritized_dic_list):
        if not found and arg_name in dic:
            kw[arg_name] = dic[arg_name]
            found = True

    if needed and not found:
        raise Exception(f'Missing {arg_name}!')

    if not found or kw[arg_name] is None:
        kw[arg_name] = default_val_f(kw)


def process_args(
    declaration: dict[str, tuple[bool, Callable[[dict[str, Any]], Any]]],
    prioritized_dic_list: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Process arguments for kwargs function.

    Args:
        declaration: Dictionary mapping argument names to (needed, default_val_f) tuples
        prioritized_dic_list: List of dictionaries to search for argument values in priority order

    Returns:
        Dictionary of processed arguments
    """
    kw = {}
    for arg_name, (needed, default_val_f) in declaration.items():
        arg_process(kw, arg_name, needed, default_val_f, prioritized_dic_list)
    return kw
