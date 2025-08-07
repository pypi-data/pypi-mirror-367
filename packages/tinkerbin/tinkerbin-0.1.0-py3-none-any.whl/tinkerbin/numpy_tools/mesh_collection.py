#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mesh collection classes for handling meshgrid data.

Provides the NpMeshCollection class for managing meshgrid data where some
arrays represent independent variables and others are dependent variables.
"""

import numpy as np
from typing import Any, Union

from .array_collection import NpArrayCollection
from ..logging import log


class NpMeshCollection(NpArrayCollection, internal_attrs=['_mesh_array_names']):
    """
    Class that stores meshgrid of independent variables and corresponding arrays of dependent variables.

    Extends NpArrayCollection to handle meshgrid data where some arrays represent
    independent variables forming a meshgrid, and others are dependent variables
    calculated based on the independent variables.
    """

    _mesh_array_names: list[
        str
    ]  # List of names of independent variables that form the meshgrid.

    def get_indep_arrays(self) -> dict[str, np.ndarray]:
        """
        Get dictionary of names and arrays corresponding to the independent variables.

        Returns:
            Dictionary mapping independent variable names to their arrays
        """
        dic = {}
        for arr_name, arr in self.get_arrays().items():
            if arr_name in self._mesh_array_names:
                dic[arr_name] = arr
        return dic

    def get_depend_arrays(self) -> dict[str, np.ndarray]:
        """
        Get dictionary of names and arrays corresponding to dependent variables.

        Returns:
            Dictionary mapping dependent variable names to their arrays
        """
        dic = {}
        for arr_name, arr in self.get_arrays().items():
            if arr_name not in self._mesh_array_names:
                dic[arr_name] = arr
        return dic

    def add_dep_variables(self, var_dic: dict[str, Any]) -> None:
        """
        Add dependent variables through dictionary of names and functions of the other variables.

        Dependent variable function evaluated for every point on the meshgrid of all other variables.

        Args:
            var_dic: Dictionary mapping variable names to functions or values
        """
        for var_name, var in var_dic.items():
            self.add_array(var_name, var, calculate=False)
        for _ in var_dic.keys():
            for var_name in var_dic.keys():
                self.calculate_array(var_name)

    @classmethod
    def mesh_from_dic(
        cls, array_dic: dict[str, Union[np.ndarray, list]]
    ) -> 'NpMeshCollection':
        """
        Construct instance by making meshgrid of arrays in dictionary.

        Args:
            array_dic: Dictionary mapping variable names to 1D arrays that will form the meshgrid

        Returns:
            New NpMeshCollection instance with meshgrid arrays
        """
        log('Setting up data arrays.')
        arr_list = list(array_dic.values())
        mesh_list = np.meshgrid(*arr_list, indexing='ij')
        some_arr = mesh_list[0]
        npm = cls(some_arr.shape)
        npm._mesh_array_names = []
        for i, arr_name in enumerate(array_dic.keys()):
            npm.add_array(arr_name, mesh_list[i])
            npm._mesh_array_names.append(arr_name)
        npm.calculate_all_data(silent=True)
        log('Setup done!')
        return npm

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            String representation showing class info, shape, mesh variables, and dependent variables
        """
        max_chars = 5000  # Truncate string at max_chars characters.
        cls = self.__class__
        string = f'<{cls.__qualname__} {id(self)}>\n\tshape: {self.shape}\n\tmesh variables: {list(self.get_indep_arrays().keys())}\n\tdependent variables: {list(self.get_depend_arrays().keys())}'
        arrays = self.get_arrays().items()
        if arrays:
            string += '\n' + '\n'.join(str(array) for array in arrays)
        if len(string) > max_chars:
            return string[:max_chars] + ' (print truncated)'
        else:
            return string

    def slice_iterator(
        self,
        slice_axes: Union[str, list[str]] = None,
        fixed_axes: dict[str, Union[int, slice]] = None,
        synced_axes: dict[str, str] = None,
    ) -> tuple:
        """
        Return iterator of array slices. Iterate over all combinations of the return slice within the meshgrid.

        Args:
            slice_axes: Axis names to slice over (return full slices for these)
            fixed_axes: Axis names and their fixed values or slices
            synced_axes: Axis names that should be synchronized with other axes

        Yields:
            Tuple slices for accessing the arrays
        """
        if slice_axes is None:
            slice_axes = []
        if fixed_axes is None:
            fixed_axes = {}
        if synced_axes is None:
            synced_axes = {}

        if isinstance(slice_axes, str):
            slice_axes = [slice_axes]

        # Make slice inverse of return slice, to iterate over.
        inverse_slice = ()
        for axis_nr, axis_name in enumerate(self._mesh_array_names):
            if axis_name in slice_axes:
                inverse_slice += (0,)
            elif axis_name in fixed_axes:
                inverse_slice += (fixed_axes[axis_name],)
            elif axis_name in synced_axes:
                inverse_slice += (0,)
            else:
                inverse_slice += (slice(None),)

        # Iterate over all remaining degrees of freedom.
        iterator_arr = np.zeros(self._dummy_array[inverse_slice].shape)
        for idx, _ in np.ndenumerate(iterator_arr):
            return_slice = list(idx)
            for axis_nr, axis_name in enumerate(self._mesh_array_names):
                if axis_name in slice_axes:
                    return_slice.insert(axis_nr, slice(None))
                elif axis_name in fixed_axes:
                    if not isinstance(fixed_axes[axis_name], slice):
                        return_slice.insert(axis_nr, fixed_axes[axis_name])
                    else:
                        axis_length = self.shape[axis_nr]
                        axis_linspace = np.linspace(
                            0, axis_length - 1, axis_length, dtype=int
                        )
                        sliced_axis_linspace = axis_linspace[fixed_axes[axis_name]]
                        return_slice[axis_nr] = sliced_axis_linspace[
                            return_slice[axis_nr]
                        ]
                elif axis_name in synced_axes:
                    return_slice.insert(axis_nr, 0)
            for axis_nr, axis_name in enumerate(self._mesh_array_names):
                if axis_name in synced_axes:
                    indep_ax = synced_axes[axis_name]
                    indep_ax_idx = self._mesh_array_names.index(indep_ax)
                    return_slice[axis_nr] = return_slice[indep_ax_idx]
            yield tuple(return_slice)
