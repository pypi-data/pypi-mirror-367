#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dictionary utility functions.

Provides helper functions for working with dictionaries including
key validation, dictionary merging, and other common dictionary operations.
"""

import copy
from typing import Any

from .logging import log


def dic_has_keys(dic: dict[str, Any], key_list: list[str]) -> bool:
    """
    Check if all keys in list are present in dictionary.

    Args:
        dic: Dictionary to check
        key_list: List of keys to verify presence of

    Returns:
        True if all keys in key_list are present in dic, False otherwise
    """
    return set(key_list) <= set(list(dic.keys()))


def dic_has_only_keys(dic: dict[str, Any], key_list: list[str]) -> bool:
    """
    Check if all keys in list are present in dictionary and no other keys are present.

    Args:
        dic: Dictionary to check
        key_list: List of keys that should be the only keys present

    Returns:
        True if dic contains exactly the keys in key_list, False otherwise
    """
    return set(key_list) == set(list(dic.keys()))


def deepcopy_dic_except(
    dic: dict[str, Any], shallow_args: list[str] = None, except_args: list[str] = None
) -> dict[str, Any]:
    """
    Selective shallow, deep or not copy items in dictionary.

    Args:
        dic: Dictionary to copy
        shallow_args: List of keys to shallow copy (default: empty list)
        except_args: List of keys to exclude from copying (default: empty list)

    Returns:
        New dictionary with selective copying applied
    """
    if shallow_args is None:
        shallow_args = []
    if except_args is None:
        except_args = []

    new_dic = {}
    for arg_name, arg_val in dic.items():
        if arg_name in shallow_args:
            new_dic[arg_name] = dic[arg_name]
        elif arg_name in except_args:
            pass
        else:
            new_dic[arg_name] = copy.deepcopy(arg_val)
    return new_dic


def recursive_key_search(
    dic: dict[str, Any],
    search_key: str,
    root_key: str = '',
    searched_list: list[dict] = None,
) -> None:
    """
    Recursively search for key in nested dictionary.

    Args:
        dic: Dictionary to search in
        search_key: Key to search for
        root_key: Root path for logging (used internally for recursion)
        searched_list: List of already searched dictionaries to avoid infinite loops
    """
    if searched_list is None:
        searched_list = []

    for key, val in dic.items():
        if key == search_key:
            if root_key == '':
                log(key)
            else:
                log(root_key + '/' + str(key))
        if isinstance(val, dict) and val not in searched_list:
            searched_list.append(val)
            recursive_key_search(
                val,
                search_key,
                root_key=root_key + '/' + str(key),
                searched_list=searched_list,
            )
