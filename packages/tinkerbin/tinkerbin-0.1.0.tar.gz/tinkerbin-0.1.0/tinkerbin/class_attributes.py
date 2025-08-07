#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for class and instance attribute inspection.

Provides functions to extract and analyze different types of attributes
from classes and instances, including instantiated attributes, annotated
attributes, and all attributes.
"""

from typing import Any


def get_inst_attrs(cls: Any, ignore_internal: bool = True) -> dict[str, Any]:
    """
    Get dictionary containing names and values of instantiated (class or instance) attributes.

    Args:
        cls: Class or instance to get attributes from
        ignore_internal: If True, ignore attributes starting and ending with '__'

    Returns:
        Dictionary containing attribute names and values
    """
    attr_dic = {}
    possible_attr_names = dir(cls)
    for attr_name in possible_attr_names:
        if hasattr(cls, attr_name):
            # If ignore_internal, ignore attributes starting and ending with '__'
            if not ignore_internal or (
                not attr_name.startswith('__') and not attr_name.endswith('__')
            ):
                attr = getattr(cls, attr_name)

                # Not callable are attributes.
                if not callable(attr):
                    attr_dic[attr_name] = attr

                # If lambda function, consider it an attribute.
                elif hasattr(attr, '__name__') and attr.__name__ == '<lambda>':
                    attr_dic[attr_name] = attr

    return attr_dic


def get_ann_attrs(cls: Any, ignore_internal: bool = True) -> dict[str, Any]:
    """
    Get dictionary containing names and types of annotated (class or instance) attributes.

    Args:
        cls: Class or instance to get annotated attributes from
        ignore_internal: If True, ignore attributes starting and ending with '__'

    Returns:
        Dictionary containing annotated attribute names and types
    """
    ann_attr_dic = {}
    if hasattr(cls, '__annotations__'):
        all_ann_attr_dic = cls.__annotations__
        for attr_name, attr_val in all_ann_attr_dic.items():
            # If ignore_internal, ignore attributes starting and ending with '__'
            if not (ignore_internal) or not (
                attr_name.startswith('__') and attr_name[0].endswith('__')
            ):
                ann_attr_dic[attr_name] = attr_val

    # Annotated attributes of parent classes are not directly accessible, so get them recursively.
    parents = ()
    if hasattr(cls, '__bases__'):
        parents = cls.__bases__
    elif hasattr(cls, '__class__') and hasattr(cls.__class__, '__bases__'):
        parents = cls.__class__.__bases__
    for parent in parents:
        if parent is not object:
            parent_ann_attr_dic = get_ann_attrs(parent, ignore_internal)
            ann_attr_dic = {**ann_attr_dic, **parent_ann_attr_dic}

    return ann_attr_dic


def get_all_attrs(cls: Any, ignore_internal: bool = True) -> dict[str, Any]:
    """
    Get dictionary containing names and values/types of all (instantiated and annotated) attributes.

    Args:
        cls: Class or instance to get all attributes from
        ignore_internal: If True, ignore attributes starting and ending with '__'

    Returns:
        Dictionary containing all attribute names and values/types.
        Instance attributes overwrite class attributes if same name.
    """
    inst_attr_dic = get_inst_attrs(cls, ignore_internal)
    ann_attr_dic = get_ann_attrs(cls, ignore_internal)

    # Instance attributes overwrite class attributes if same name.
    all_attr_dic = {**ann_attr_dic, **inst_attr_dic}

    return all_attr_dic
