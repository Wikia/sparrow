# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from common.utils import camel2snake

class TestCamel2Snake(TestCase):
    def test_camel_simple(self):
        self.assertEqual(camel2snake('SimpleCamel'), 'simple_camel')
        self.assertEqual(camel2snake('Camel'), 'camel')
        self.assertEqual(camel2snake('ABCamel'), 'ab_camel')
        self.assertEqual(camel2snake('XYZCamel'), 'xyz_camel')
        self.assertEqual(camel2snake('TripleCamelCase'), 'triple_camel_case')
        self.assertEqual(camel2snake('mixedCamelCase'), 'mixed_camel_case')
        self.assertEqual(camel2snake('UnderScoreEnd_'), 'under_score_end_')
        self.assertEqual(camel2snake('_BeginUnderScore'), '_begin_under_score')
        self.assertEqual(camel2snake('_BothUnderScore_'), '_both_under_score_')
