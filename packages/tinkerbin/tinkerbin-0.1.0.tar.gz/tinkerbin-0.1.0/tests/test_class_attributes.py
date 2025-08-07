#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for class attribute functions.
Tests the get_inst_attrs, get_ann_attrs, and get_all_attrs functions.
"""

import unittest

import tinkerbin as tb
from tinkerbin.class_attributes import get_inst_attrs, get_ann_attrs, get_all_attrs


class TestClassAttributes(unittest.TestCase):
    """Test class for class attribute functions."""

    def setUp(self):
        """Set up test classes and instances."""

        class A:
            AA1: int
            AI1: float = 0
            AI2 = 1
            AI3 = lambda x, y: None
            AI4 = lambda x=0, y=1: None

            def AM1(x, y):
                pass

            def AM2(x: int, y=0, z=None):
                pass

            @classmethod
            def AM3(cls, x, y):
                pass

            @classmethod
            def AM4(cls, x: int, y=0, z=None):
                pass

            def AM5(self, x, y):
                pass

            def AM6(self, x: int, y=0, z=None):
                pass

        class B(A):
            BA1: int
            BI1: float = 0
            BI2 = 1
            BI3 = lambda x, y: None
            BI4 = lambda x=0, y=1: None

            def BM1(x, y):
                pass

            def BM2(x: int, y=0, z=None):
                pass

            @classmethod
            def BM3(cls, x, y):
                pass

            @classmethod
            def BM4(cls, x: int, y=0, z=None):
                pass

            def BM5(self, x, y):
                pass

            def BM6(self, x: int, y=0, z=None):
                pass

        self.A = A
        self.B = B

        # Create instances with additional attributes
        self.a1 = A()
        self.a1.ai1 = 0
        self.a1.ai2 = lambda x, y: None
        self.a1.ai3 = lambda x=0, y=1: None

        self.b1 = B()
        self.b1.bi1 = 0
        self.b1.bi2 = lambda x, y: None
        self.b1.bi3 = lambda x=0, y=1: None

        # Create instances with overridden attributes
        self.a2 = A()
        self.a2.AA1 = 1
        self.a2.AI1 = 1
        self.a2.AI2 = 1
        self.a2.AI3 = 1
        self.a2.AI4 = 1
        self.a2.AM1 = 1
        self.a2.AM2 = 1
        self.a2.AM3 = 1
        self.a2.AM4 = 1
        self.a2.AM5 = 1
        self.a2.AM6 = 1

        self.b2 = B()
        self.b2.AA1 = 1
        self.b2.AI1 = 1
        self.b2.AI2 = 1
        self.b2.AI3 = 1
        self.b2.AI4 = 1
        self.b2.AM1 = 1
        self.b2.AM2 = 1
        self.b2.AM3 = 1
        self.b2.AM4 = 1
        self.b2.AM5 = 1
        self.b2.AM6 = 1
        self.b2.BA1 = 1
        self.b2.BI1 = 1
        self.b2.BI2 = 1
        self.b2.BI3 = 1
        self.b2.BI4 = 1
        self.b2.BM1 = 1
        self.b2.BM2 = 1
        self.b2.BM3 = 1
        self.b2.BM4 = 1
        self.b2.BM5 = 1
        self.b2.BM6 = 1

    def test_get_inst_attrs_class_A(self):
        """Test get_inst_attrs on class A."""
        result = get_inst_attrs(self.A)
        expected_keys = ['AI1', 'AI2', 'AI3', 'AI4']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_ann_attrs_class_A(self):
        """Test get_ann_attrs on class A."""
        result = get_ann_attrs(self.A)
        expected_keys = ['AA1', 'AI1']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_all_attrs_class_A(self):
        """Test get_all_attrs on class A."""
        result = get_all_attrs(self.A)
        expected_keys = ['AA1', 'AI1', 'AI2', 'AI3', 'AI4']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_inst_attrs_class_B(self):
        """Test get_inst_attrs on class B (inheritance)."""
        result = get_inst_attrs(self.B)
        expected_keys = ['BI1', 'BI2', 'BI3', 'BI4', 'AI1', 'AI2', 'AI3', 'AI4']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_ann_attrs_class_B(self):
        """Test get_ann_attrs on class B (inheritance)."""
        result = get_ann_attrs(self.B)
        expected_keys = ['BA1', 'BI1', 'AA1', 'AI1']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_all_attrs_class_B(self):
        """Test get_all_attrs on class B (inheritance)."""
        result = get_all_attrs(self.B)
        expected_keys = [
            'BA1',
            'AA1',
            'BI1',
            'BI2',
            'BI3',
            'BI4',
            'AI1',
            'AI2',
            'AI3',
            'AI4',
        ]
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_inst_attrs_instance_a1(self):
        """Test get_inst_attrs on instance a1."""
        result = get_inst_attrs(self.a1)
        expected_keys = ['ai1', 'ai2', 'ai3', 'AI1', 'AI2', 'AI3', 'AI4']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_ann_attrs_instance_a1(self):
        """Test get_ann_attrs on instance a1."""
        result = get_ann_attrs(self.a1)
        expected_keys = ['AA1', 'AI1']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_all_attrs_instance_a1(self):
        """Test get_all_attrs on instance a1."""
        result = get_all_attrs(self.a1)
        expected_keys = ['AA1', 'AI1', 'ai1', 'ai2', 'ai3', 'AI1', 'AI2', 'AI3', 'AI4']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_inst_attrs_instance_b1(self):
        """Test get_inst_attrs on instance b1."""
        result = get_inst_attrs(self.b1)
        expected_keys = [
            'bi1',
            'bi2',
            'bi3',
            'BI1',
            'BI2',
            'BI3',
            'BI4',
            'AI1',
            'AI2',
            'AI3',
            'AI4',
        ]
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_ann_attrs_instance_b1(self):
        """Test get_ann_attrs on instance b1."""
        result = get_ann_attrs(self.b1)
        expected_keys = ['BA1', 'BI1', 'AA1', 'AI1']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_all_attrs_instance_b1(self):
        """Test get_all_attrs on instance b1."""
        result = get_all_attrs(self.b1)
        expected_keys = [
            'BA1',
            'BI1',
            'AA1',
            'AI1',
            'bi1',
            'bi2',
            'bi3',
            'BI1',
            'BI2',
            'BI3',
            'BI4',
            'AI1',
            'AI2',
            'AI3',
            'AI4',
        ]
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_inst_attrs_instance_a2(self):
        """Test get_inst_attrs on instance a2 with overridden attributes."""
        result = get_inst_attrs(self.a2)
        expected_keys = [
            'AA1',
            'AI1',
            'AI2',
            'AI3',
            'AI4',
            'AM1',
            'AM2',
            'AM3',
            'AM4',
            'AM5',
            'AM6',
        ]
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_ann_attrs_instance_a2(self):
        """Test get_ann_attrs on instance a2 with overridden attributes."""
        result = get_ann_attrs(self.a2)
        expected_keys = ['AA1', 'AI1']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_all_attrs_instance_a2(self):
        """Test get_all_attrs on instance a2 with overridden attributes."""
        result = get_all_attrs(self.a2)
        expected_keys = [
            'AA1',
            'AI1',
            'AI2',
            'AI3',
            'AI4',
            'AM1',
            'AM2',
            'AM3',
            'AM4',
            'AM5',
            'AM6',
        ]
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_inst_attrs_instance_b2(self):
        """Test get_inst_attrs on instance b2 with overridden attributes."""
        result = get_inst_attrs(self.b2)
        expected_keys = [
            'BA1',
            'BI1',
            'BI2',
            'BI3',
            'BI4',
            'BM1',
            'BM2',
            'BM3',
            'BM4',
            'BM5',
            'BM6',
            'AA1',
            'AI1',
            'AI2',
            'AI3',
            'AI4',
            'AM1',
            'AM2',
            'AM3',
            'AM4',
            'AM5',
            'AM6',
        ]
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_ann_attrs_instance_b2(self):
        """Test get_ann_attrs on instance b2 with overridden attributes."""
        result = get_ann_attrs(self.b2)
        expected_keys = ['BA1', 'BI1', 'AA1', 'AI1']
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))

    def test_get_all_attrs_instance_b2(self):
        """Test get_all_attrs on instance b2 with overridden attributes."""
        result = get_all_attrs(self.b2)
        expected_keys = [
            'BA1',
            'BI1',
            'BI2',
            'BI3',
            'BI4',
            'BM1',
            'BM2',
            'BM3',
            'BM4',
            'BM5',
            'BM6',
            'AA1',
            'AI1',
            'AI2',
            'AI3',
            'AI4',
            'AM1',
            'AM2',
            'AM3',
            'AM4',
            'AM5',
            'AM6',
        ]
        self.assertTrue(tb.dic_has_only_keys(result, expected_keys))


if __name__ == '__main__':
    unittest.main()
