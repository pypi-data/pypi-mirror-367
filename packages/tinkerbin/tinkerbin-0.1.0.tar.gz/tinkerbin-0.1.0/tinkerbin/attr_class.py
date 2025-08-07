#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base class for attribute tracking and management.

Provides the AttrClass base class that enables automatic tracking of class
and instance attributes while filtering out internal attributes.
"""

from typing import Any, Optional
from .class_attributes import get_inst_attrs, get_ann_attrs, get_all_attrs


class AttrClass:
    """
    A base class that provides attribute tracking and management functionality.

    This class keeps track of its attributes and provides methods to get, set, and
    manage both class and instance attributes while filtering out internal attributes.
    """

    _internal_attributes: set[str] = {
        '_internal_attributes'
    }  # Set of attributes to be ignored when getting list of attributes.

    @classmethod
    def __init_subclass__(
        cls, internal_attrs: Optional[list[str]] = None, **kwargs: Any
    ) -> None:
        """
        Initialize subclass with custom internal attributes.

        Subclasses can specify their own internal attributes in the inheritance declaration.

        Args:
            internal_attrs: List of attribute names to be treated as internal
            **kwargs: Additional keyword arguments passed to parent __init_subclass__
        """
        if internal_attrs is None:
            internal_attrs = []
        super().__init_subclass__(**kwargs)
        parent_internal_attrs = cls._internal_attributes
        cls._internal_attributes = set()
        for attr in parent_internal_attrs:
            cls._internal_attributes.add(attr)
        for attr in internal_attrs:
            cls._internal_attributes.add(attr)

    @classmethod
    def from_dic(cls, attr_dic: dict[str, Any]) -> 'AttrClass':
        """
        Construct an instance with attributes from dictionary.

        Args:
            attr_dic: Dictionary containing attribute names and values

        Returns:
            New instance of the class with attributes set from the dictionary
        """
        ac = cls()
        for attr_name, attr_val in attr_dic.items():
            ac.set_attribute(attr_name, attr_val)
        return ac

    def to_dic(self) -> dict[str, Any]:
        """
        Get dictionary representation of instance attributes.

        Returns:
            Dictionary containing instance attribute names and values
        """
        return self.get_inst_attrs()

    def set_attrs_from_dic(self, attr_dic: dict[str, Any]) -> None:
        """
        Set class attributes supplied by dictionary.

        Args:
            attr_dic: Dictionary containing attribute names and values to set
        """
        obj_attr_dic = self.get_all_attrs()
        for attr_name, attr_val in attr_dic.items():
            if attr_name in obj_attr_dic:
                self.set_attribute(attr_name, attr_val)

    @classmethod
    def set_cls_attribute(cls, attr_name: str, attr_value: Any) -> None:
        """
        Add an attribute to the class.

        Args:
            attr_name: Name of the attribute to set
            attr_value: Value to assign to the attribute
        """
        cls.__dict__[attr_name] = attr_value

    def set_attribute(self, attr_name: str, attr_value: Any) -> None:
        """
        Add an attribute to an instance.

        Args:
            attr_name: Name of the attribute to set
            attr_value: Value to assign to the attribute
        """
        self.__dict__[attr_name] = attr_value

    @classmethod
    def get_cls_inst_attrs(cls) -> dict[str, Any]:
        """
        Get dictionary of names and values of instantiated attributes of class.

        Returns:
            Dictionary containing class instantiated attribute names and values,
            excluding internal attributes
        """
        attr_dic = get_inst_attrs(cls)
        proper_attr_dic = {}
        for attr_name, attr_val in attr_dic.items():
            if attr_name not in cls._internal_attributes:
                proper_attr_dic[attr_name] = attr_val
        return proper_attr_dic

    def get_inst_attrs(self) -> dict[str, Any]:
        """
        Get dictionary of names and values of instantiated attributes of instance.

        Returns:
            Dictionary containing instance instantiated attribute names and values,
            excluding internal attributes
        """
        attr_dic = get_inst_attrs(self)
        proper_attr_dic = {}
        for attr_name, attr_val in attr_dic.items():
            if attr_name not in self._internal_attributes:
                proper_attr_dic[attr_name] = attr_val
        return proper_attr_dic

    @classmethod
    def get_cls_ann_attrs(cls) -> dict[str, Any]:
        """
        Get dictionary of names and values of defined annotated attributes of class.

        Returns:
            Dictionary containing class annotated attribute names and types,
            excluding internal attributes
        """
        attr_dic = get_ann_attrs(cls)
        proper_attr_dic = {}
        for attr_name, attr_val in attr_dic.items():
            if attr_name not in cls._internal_attributes:
                proper_attr_dic[attr_name] = attr_val
        return proper_attr_dic

    def get_ann_attrs(self) -> dict[str, Any]:
        """
        Get dictionary of names and values of defined annotated attributes of instance.

        Returns:
            Dictionary containing instance annotated attribute names and types,
            excluding internal attributes
        """
        attr_dic = get_ann_attrs(self)
        proper_attr_dic = {}
        for attr_name, attr_val in attr_dic.items():
            if attr_name not in self._internal_attributes:
                proper_attr_dic[attr_name] = attr_val
        return proper_attr_dic

    @classmethod
    def get_cls_all_attrs(cls) -> dict[str, Any]:
        """
        Get dictionary of names and values of all attributes of class.

        Returns:
            Dictionary containing all class attribute names and values,
            excluding internal attributes
        """
        attr_dic = get_all_attrs(cls)
        proper_attr_dic = {}
        for attr_name, attr_val in attr_dic.items():
            if attr_name not in cls._internal_attributes:
                proper_attr_dic[attr_name] = attr_val
        return proper_attr_dic

    def get_all_attrs(self) -> dict[str, Any]:
        """
        Get dictionary of names and values of all attributes of instance.

        Instance attributes take precedence over class attributes if same name.

        Returns:
            Dictionary containing all instance attribute names and values,
            excluding internal attributes
        """
        attr_dic = get_all_attrs(self)
        proper_attr_dic = {}
        for attr_name, attr_val in attr_dic.items():
            if attr_name not in self._internal_attributes:
                proper_attr_dic[attr_name] = attr_val
        return proper_attr_dic

    @classmethod
    def get_cls_attr(cls, attr_name: str) -> Any:
        """
        Get attribute from class.

        Args:
            attr_name: Name of the attribute to retrieve

        Returns:
            Value of the requested class attribute
        """
        return cls.__dict__[attr_name]

    def get_attr(self, attr_name: str) -> Any:
        """
        Get attribute from instance.

        Args:
            attr_name: Name of the attribute to retrieve

        Returns:
            Value of the requested instance attribute
        """
        return self.__dict__[attr_name]

    def __repr__(self) -> str:
        """
        String representation of instance.

        Returns:
            String representation showing class name, instance ID, and attributes
        """
        max_chars = 5000  # Truncate string at max_chars characters.
        cls = self.__class__
        string = f'<{cls.__qualname__} {id(self)}: {self.get_inst_attrs()}>'
        if len(string) > max_chars:
            return string[:max_chars] + ' (print truncated)'
        else:
            return string

    def __str__(self) -> str:
        """
        Calling print on instance returns instance string representations.

        Returns:
            String representation of the instance
        """
        return self.__repr__()
