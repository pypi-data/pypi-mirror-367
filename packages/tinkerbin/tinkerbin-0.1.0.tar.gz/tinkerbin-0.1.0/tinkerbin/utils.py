#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General utility functions for tinkerbin.

Provides miscellaneous helper functions including script name retrieval
and other common utilities used across the package.
"""

from typing import Any


def get_script_name(suffix: bool = False) -> str:
    """
    Get main script file name.

    Args:
        suffix: Whether to include file extension

    Returns:
        Name of the main script file, with or without extension
    """
    import os
    import __main__

    file_path = __main__.__file__
    file_name = os.path.basename(file_path)
    if not suffix:
        file_name = os.path.splitext(file_name)[0]
    return file_name


def flatten(lst: Any) -> list[Any]:
    """
    Flatten arbitrarily nested list of lists.

    Args:
        lst: Nested list structure to flatten

    Returns:
        Flattened list containing all elements from nested structure
    """
    from collections.abc import Iterable

    if isinstance(lst, Iterable) and not isinstance(lst, (str, bytes)):
        return [el for sub_lst in lst for el in flatten(sub_lst)]
    else:
        return [lst]


def ClassFactory(class_name: str, BaseClass: type = object) -> type:
    """
    Factory for making classes.

    Args:
        class_name: Name for the new class
        BaseClass: Base class to inherit from (default: object)

    Returns:
        New class type with the specified name and base class
    """
    new_class = type(class_name, (BaseClass,), {})
    return new_class


def repeating(lst: list[Any]) -> list[Any]:
    """
    Make repeating list out of any list.

    Creates a list that cycles through its elements when accessed with indices
    beyond its length using modulo arithmetic.

    Args:
        lst: List to make repeating

    Returns:
        List that repeats its elements cyclically when accessed
    """
    rep_lst_cls = ClassFactory('RepeatingList', list)
    rep_lst = rep_lst_cls(lst)
    rep_lst.lst = lst
    rep_lst.__class__.__getitem__ = lambda self, i: self.lst[i % len(self.lst)]
    return rep_lst
