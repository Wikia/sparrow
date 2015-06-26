# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from metrics.compare import CompareResult
from metrics.values import Stats


class TestCompareResult(TestCase):
    def test_result_value(self):
        a = Stats([1])
        b = Stats([2])
        self.assertEqual(CompareResult('x1',[a,b]).result, -1, 'worse')
        self.assertEqual(CompareResult('x1',[b,a]).result, 1, 'better')
        self.assertEqual(CompareResult('x1',[a,a]).result, 0, 'same')
