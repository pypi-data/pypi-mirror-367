#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Array collection classes for managing multiple numpy arrays.

Provides the NpArrayCollection class for storing, managing, and performing
calculations on collections of numpy arrays that share the same shape.
"""

import math
import re
from typing import Any, Union, Optional

import numpy as np

from ..attr_class import AttrClass
from ..logging import log
from ..function_evaluation import eval_if_func


class NpArrayCollection(
    AttrClass, internal_attrs=['_loop_print_subdiv', 'shape', '_dummy_array', '_arrays']
):
    """
    Collection class for managing multiple numpy arrays of the same shape.

    This class provides functionality to store, manage, and perform calculations
    on collections of numpy arrays that share the same shape. It supports
    automatic calculation of array values based on functions of other arrays.
    """

    _loop_print_subdiv: int = (
        10  # How many subdivisions for printouts during loop prints.
    )

    shape: tuple  # Shape of arrays.
    _dummy_array: np.typing.NDArray  # Empty array with same shape.
    _arrays: dict  # Dictionary of arrays.

    def __init__(self, shape: tuple) -> None:
        """
        Initialize with arrays of specified shape.

        When initializing, set all class attributes to zero numpy arrays of specified shape.

        Args:
            shape: Shape tuple for all arrays in the collection
        """
        self.shape = tuple(shape)
        self._arrays = {}
        self._dummy_array = np.zeros(shape)
        self.initialize_arrays()
        self.calculate_all_data(silent=True)

    @classmethod
    def from_dic(
        cls, array_dic: dict[str, Union[np.ndarray, list]]
    ) -> 'NpArrayCollection':
        """
        Construct instance based on dictionary of existing arrays of equal shape.

        Args:
            array_dic: Dictionary mapping array names to arrays or lists

        Returns:
            New NpArrayCollection instance with arrays from the dictionary
        """
        log('Setting up data arrays.')

        # Iterate until list or numpy array is found, use its shape.
        shape = (1,)
        found_shape = False
        for arr in array_dic.values():
            if isinstance(arr, np.ndarray) and not found_shape:
                shape = arr.shape
                found_shape = True
            elif isinstance(arr, list) and not found_shape:
                shape = np.array(arr).shape
                found_shape = True
        npa = cls(shape)

        # For all arguments, add array.
        for array_name, arr in array_dic.items():
            npa.add_array(array_name, arr, calculate=False)

        npa.calculate_all_data(silent=True)
        log('Setup done!')
        return npa

    def _make_empty_array(self, dtype: Optional[type] = None) -> np.ndarray:
        """
        Make new, empty array. Convert int array to float array, to allow NaN.

        Args:
            dtype: Data type for the array (int will be converted to float)

        Returns:
            Empty array filled with None values
        """
        if dtype is int:
            dtype = float
        return np.full(self.shape, None, dtype=dtype)

    def initialize_arrays(self) -> None:
        """
        Set all class attributes to zero numpy arrays of same shape.

        Initializes arrays based on both instantiated and annotated class attributes.
        """
        inst_attr_dic = self.get_cls_inst_attrs()
        for attr_name, attr_val in inst_attr_dic.items():
            self.add_array(attr_name, attr_val, calculate=False)

        ann_attr_dic = self.get_cls_ann_attrs()
        for attr_name, attr_val in ann_attr_dic.items():
            # If array not already added.
            if attr_name not in self.get_arrays():
                # If annotated attribute is numpy array, use the dtype of the array.
                matches = re.findall(r'numpy\.([a-zA-Z]+)[0-9]+', str(attr_val))
                if len(matches) > 0:
                    dtype = matches[0] + '_'

                # Else set dtype to the declared variable type.
                else:
                    dtype = attr_val

                self.add_array(
                    attr_name, self._make_empty_array(dtype), calculate=False
                )

    def get_arrays(self) -> dict[str, np.ndarray]:
        """
        Get dictionary of numpy arrays.

        Returns:
            Dictionary mapping array names to numpy arrays
        """
        return self._arrays

    def get_array(self, array_name: str) -> np.ndarray:
        """
        Get array by name.

        Args:
            array_name: Name of the array to retrieve

        Returns:
            The requested numpy array
        """
        return self.get_arrays()[array_name]

    def set_value(self, array_name: str, idx: tuple, val: Any) -> None:
        """
        Set element of array at index to value.

        Args:
            array_name: Name of the array to modify
            idx: Index tuple specifying the element location
            val: Value to set at the specified index
        """
        self.get_array(array_name)[idx] = val

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            String representation showing class info, shape, and array names
        """
        max_chars = 5000  # Truncate string at max_chars characters.
        cls = self.__class__
        string = f'<{cls.__qualname__} {id(self)}>\n\tshape: {self.shape}\n\tarrays: {list(self._arrays.keys())}'
        arrays = self.get_arrays().items()
        if arrays:
            string += '\n' + '\n'.join(str(array) for array in arrays)
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

    def add_array(
        self, array_name: str, arr: Union[np.ndarray, list, Any], calculate: bool = True
    ) -> None:
        """
        Add an array to instance, calculate if chosen.

        Args:
            array_name: Name for the new array
            arr: Array data (numpy array, list, or scalar value)
            calculate: Whether to perform calculations after adding

        Raises:
            Exception: If array shape doesn't match collection shape
        """
        if isinstance(arr, list):
            arr = np.array(arr)

        if isinstance(arr, np.ndarray):
            if arr.shape == self.shape:
                self.set_attribute(array_name, arr)
                self._arrays[array_name] = self.get_attr(array_name)
            else:
                raise Exception(
                    f'Attempted to add array to NpArrayCollection of shape <{self.shape}>, but array <{array_name}> has shape <{arr.shape}>.'
                )
        else:
            self.set_attribute(array_name, np.full(self.shape, arr))
            self._arrays[array_name] = self.get_attr(array_name)

        if calculate:
            self.calculate_array(array_name)

    def add_arrays(
        self, arr_dic: dict[str, Union[np.ndarray, list, Any]], calculate: bool = True
    ) -> None:
        """
        Add arrays from dictionary to instance, calculate if chosen.

        Args:
            arr_dic: Dictionary mapping array names to array data
            calculate: Whether to perform calculations after adding
        """
        for array_name, arr in arr_dic.items():
            self.add_array(array_name, arr, calculate)

    def idx_to_dic(self, idx: tuple) -> dict[str, Any]:
        """
        Get dictionary with values of all arrays at specified index.

        Args:
            idx: Index tuple specifying the location

        Returns:
            Dictionary mapping array names to values at the specified index
        """
        dic = {}
        for arr_name, arr in self.get_arrays().items():
            dic[arr_name] = arr.item(*idx)
        return dic

    def idx_to_str(self, idx: tuple) -> str:
        """
        Generate string with values of all arrays at specified index.

        Args:
            idx: Index tuple specifying the location

        Returns:
            String representation of all array values at the index
        """
        string = '\n'.join(
            f'{arr_name}: {str(val)}' for arr_name, val in self.idx_to_dic(idx).items()
        )
        return string

    def idx_iterator(self) -> tuple:
        """
        Iterate through the array indices, returning the array index.

        Yields:
            Index tuples for all positions in the arrays
        """
        for idx, _ in np.ndenumerate(self._dummy_array):
            yield idx

    def idx_is_edge(self, idx: tuple) -> bool:
        """
        Check whether index is edge case.

        Args:
            idx: Index tuple to check

        Returns:
            True if the index is at the edge of the array in all dimensions
        """
        all_idx_are_edge = True
        for idx_pos, idx_val in enumerate(idx):
            current_idx_is_edge = idx_val == 0 or idx_val == self.shape[idx_pos] - 1
            all_idx_are_edge &= current_idx_is_edge
        return all_idx_are_edge

    def idx_is_special(self, idx: tuple) -> bool:
        """
        Check whether index is special case for progress reporting.

        Checks if index is edge case, or if an axis has size e.g. 1000 whether
        index is whole number of 100s in that axis.

        Args:
            idx: Index tuple to check

        Returns:
            True if the index should be considered special for progress reporting
        """
        if self.idx_is_edge(idx):
            return False
        all_idx_are_special = True
        for idx_pos, idx_val in enumerate(idx):
            current_idx_is_special = idx_val == 0
            current_idx = self.shape[idx_pos]
            current_idx_order = int(math.floor(math.log10(current_idx)))
            if current_idx_order >= 1:
                current_idx_round = int(
                    round(current_idx / 10**current_idx_order, 0)
                    * 10**current_idx_order
                )
                current_idx_multi = int(current_idx_round / self._loop_print_subdiv)
                current_idx_is_special |= (idx_val + 1) % current_idx_multi == 0
            all_idx_are_special &= current_idx_is_special
        return all_idx_are_special

    def idx_str(self, idx: tuple) -> str:
        """
        Get index printed as string.

        Args:
            idx: Index tuple to format

        Returns:
            Formatted string representation of the index
        """
        idx_str = '('
        for idx_pos, idx_len in enumerate(self.shape):
            idx_str += str(idx[idx_pos] + 1).rjust(len(str(idx_len))) + ', '
        idx_str = idx_str[:-2] + ')'
        return idx_str

    def get_progress_from_idx(self, idx: tuple) -> float:
        """
        Get progress from index.

        Args:
            idx: Index tuple to calculate progress for

        Returns:
            Progress as a float between 0 and 1
        """
        current = 0
        total = 0
        for t_idx in self.idx_iterator():
            if t_idx == idx:
                current = total
            total += 1
        return current / (total - 1)

    def print_loop_progress(self, idx: tuple) -> None:
        """
        Get string of loop index progress.

        Args:
            idx: Current index in the loop
        """
        if self.idx_is_edge(idx) or self.idx_is_special(idx):
            tuple_string = self.idx_str(idx) + ' of ' + str(tuple(self.shape))
            percent_str = (
                '   ['
                + str(round(self.get_progress_from_idx(idx) * 100)).rjust(3)
                + '%]'
            )
            log(tuple_string + percent_str)

    def calculate_array_idx(self, array_name: str, idx: tuple) -> None:
        """
        Calculate value of array at index based on values of other arrays at same index.

        Args:
            array_name: Name of the array to calculate
            idx: Index tuple specifying the location to calculate
        """
        array_dic = self.get_arrays()

        # Build dictionary of values (or functions) of all arrays at current index to pass to functions.
        arg_dic = {}
        for self_array_name, arr in array_dic.items():
            arg_dic[self_array_name] = arr[idx]

        array = self.get_array(array_name)
        self.set_value(array_name, idx, eval_if_func(array[idx], arg_dic))

    def calculate_array(self, array_name: str) -> None:
        """
        Calculate all values of array based on values of other arrays.

        Args:
            array_name: Name of the array to calculate
        """
        for idx in self.idx_iterator():
            self.calculate_array_idx(array_name, idx)

        # Copy array to get updated dtype.
        arr = self.get_array(array_name)
        if arr.item(0) is not None and not callable(arr.item(0)):
            dtype = type(arr.item(0))
            new_arr = np.zeros(self.shape, dtype=dtype)
            new_arr[:] = arr
            self.add_array(array_name, new_arr, calculate=False)

    def calculate_data_idx(self, idx: tuple) -> None:
        """
        For arrays that are functions of the other arrays, calculate functions at index.

        Args:
            idx: Index tuple specifying the location to calculate
        """
        array_dic = self.get_arrays()

        # Need N^2 passes to ensure evaluating all functions that are dependent on other functions having been evaluated.
        for _ in array_dic:
            for array_name in array_dic:
                self.calculate_array_idx(array_name, idx)

    def calculate_all_data(self, silent: bool = False) -> None:
        """
        Calculate all data.

        Args:
            silent: Whether to suppress progress messages
        """
        if not silent:
            log('Calculating data.')
        array_dic = self.get_arrays()

        # Need N^2 passes to ensure evaluating all functions that are dependent on other functions having been evaluated.
        for _ in array_dic:
            for array_name, arr in array_dic.items():
                self.calculate_array(array_name)

        if not silent:
            log('Calculation done!')
