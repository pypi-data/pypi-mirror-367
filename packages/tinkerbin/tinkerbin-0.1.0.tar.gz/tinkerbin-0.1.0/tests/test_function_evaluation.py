#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for function evaluation functions.
Tests the get_func_args function.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import tinkerbin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tinkerbin.function_evaluation import get_func_args


class TestFunctionEvaluation(unittest.TestCase):
    """Test class for function evaluation functions."""

    def setUp(self):
        """Set up test functions and classes."""

        class A:
            fA1 = lambda x, y: None
            fA2 = lambda x=0, y=1: None

            def fA3(x, y):
                pass

            def fA4(x: int, y=0, z=None):
                pass

            @classmethod
            def fA5(cls, x, y):
                pass

            @classmethod
            def fA6(cls, x: int, y=0, z=None):
                pass

            def fA7(self, x, y):
                pass

            def fA8(self, x: int, y=0, z=None):
                pass

        self.A = A

        # Create instance with additional functions
        self.a1 = A()
        self.a1.f1 = lambda x, y: None
        self.a1.f2 = lambda x=0, y=1: None

        # Define standalone functions
        def f1(x, y):
            pass

        def f2(x: int, y=0, z=None):
            pass

        f3 = lambda x, y: None
        f4 = lambda x=0, y=1: None

        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.f4 = f4

    def test_standalone_functions(self):
        """Test get_func_args on standalone functions."""
        self.assertEqual(set(get_func_args(self.f1)), set(['x', 'y']))
        self.assertEqual(set(get_func_args(self.f2)), set(['x', 'y', 'z']))
        self.assertEqual(set(get_func_args(self.f3)), set(['x', 'y']))
        self.assertEqual(set(get_func_args(self.f4)), set(['x', 'y']))

    def test_class_lambda_functions(self):
        """Test get_func_args on class lambda functions."""
        self.assertEqual(set(get_func_args(self.A.fA1)), set(['x', 'y']))
        self.assertEqual(set(get_func_args(self.A.fA2)), set(['x', 'y']))

    def test_class_regular_functions(self):
        """Test get_func_args on class regular functions."""
        self.assertEqual(set(get_func_args(self.A.fA3)), set(['x', 'y']))
        self.assertEqual(set(get_func_args(self.A.fA4)), set(['x', 'y', 'z']))

    def test_class_methods(self):
        """Test get_func_args on class methods."""
        # When accessing classmethods through the class, 'cls' is already bound
        self.assertEqual(set(get_func_args(self.A.fA5)), set(['x', 'y']))
        self.assertEqual(set(get_func_args(self.A.fA6)), set(['x', 'y', 'z']))

    def test_instance_methods(self):
        """Test get_func_args on instance methods."""
        self.assertEqual(set(get_func_args(self.A.fA7)), set(['self', 'x', 'y']))
        self.assertEqual(set(get_func_args(self.A.fA8)), set(['self', 'x', 'y', 'z']))

    def test_instance_lambda_functions(self):
        """Test get_func_args on instance lambda functions."""
        self.assertEqual(set(get_func_args(self.a1.f1)), set(['x', 'y']))
        self.assertEqual(set(get_func_args(self.a1.f2)), set(['x', 'y']))


if __name__ == '__main__':
    unittest.main()
