#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for numpy tools.
Tests the slice functionality of NpMeshCollection.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import tinkerbin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tinkerbin.numpy_tools.mesh_collection import NpMeshCollection


class TestNumpyTools(unittest.TestCase):
    """Test class for numpy tools functionality."""

    def setUp(self):
        """Set up test data for slice testing."""
        # Create test dictionary similar to the original test
        self.dic = {
            'a': [1, 2],
            'b': [10, 11, 12],
            'c': [20, 21, 22],
            'd': [30, 31, 32],
            'e': [40, 41],
        }
        self.npm = NpMeshCollection.mesh_from_dic(self.dic)

    def test_slice_iterator_basic(self):
        """Test basic slice iterator functionality."""
        # Test that slice_iterator returns an iterator
        iterator = self.npm.slice_iterator(
            ['a'], synced_axes={'b': 'c', 'd': 'c'}, fixed_axes={'e': 1}
        )

        # Collect all indices from the iterator
        indices = list(iterator)

        # Verify that we get some indices back
        self.assertGreater(len(indices), 0)

        # Verify that each index is a tuple
        for idx in indices:
            self.assertIsInstance(idx, tuple)

    def test_slice_iterator_with_synced_axes(self):
        """Test slice iterator with synced axes."""
        iterator = self.npm.slice_iterator(
            ['a'], synced_axes={'b': 'c', 'd': 'c'}, fixed_axes={'e': 1}
        )
        indices = list(iterator)

        # Should have some valid indices
        self.assertGreater(len(indices), 0)

        # Each index should be a tuple with the correct number of dimensions
        for idx in indices:
            self.assertIsInstance(idx, tuple)
            self.assertEqual(len(idx), len(self.npm.shape))

    def test_slice_iterator_with_fixed_axes(self):
        """Test slice iterator with fixed axes."""
        iterator = self.npm.slice_iterator(['a'], fixed_axes={'e': 1})
        indices = list(iterator)

        # Should have some valid indices
        self.assertGreater(len(indices), 0)

        # Each index should be a tuple
        for idx in indices:
            self.assertIsInstance(idx, tuple)

    def test_slice_iterator_single_axis(self):
        """Test slice iterator with single axis as string."""
        # Test that string input is converted to list
        iterator = self.npm.slice_iterator('a', fixed_axes={'e': 1})
        indices = list(iterator)

        # Should have some valid indices
        self.assertGreater(len(indices), 0)

    def test_mesh_from_dic_creation(self):
        """Test that mesh_from_dic creates a valid NpMeshCollection."""
        self.assertIsInstance(self.npm, NpMeshCollection)
        self.assertEqual(len(self.npm._mesh_array_names), len(self.dic))

        # Check that all dictionary keys are in mesh array names
        for key in self.dic.keys():
            self.assertIn(key, self.npm._mesh_array_names)

    def test_mesh_shape_consistency(self):
        """Test that the mesh has the expected shape."""
        expected_shape = tuple(len(arr) for arr in self.dic.values())
        self.assertEqual(self.npm.shape, expected_shape)

    def test_get_indep_arrays(self):
        """Test getting independent arrays."""
        indep_arrays = self.npm.get_indep_arrays()

        # Should have the same keys as the original dictionary
        self.assertEqual(set(indep_arrays.keys()), set(self.dic.keys()))

    def test_get_depend_arrays(self):
        """Test getting dependent arrays."""
        depend_arrays = self.npm.get_depend_arrays()

        # Initially should be empty since we haven't added any dependent variables
        self.assertEqual(len(depend_arrays), 0)


if __name__ == '__main__':
    unittest.main()
