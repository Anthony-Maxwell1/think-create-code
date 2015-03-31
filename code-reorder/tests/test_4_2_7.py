# -*- coding: utf-8 -*-
'''

USAGE:
    python -m unittest tests.test_4_2_7

    coverage run --include=./*.py  -m unittest tests.test_4_2_7
'''
import unittest
import json

import code_reorder_4_2_7 as code_reorder


class TestGradingIncorrect(unittest.TestCase):

    def test_incorrect_empty(self):
        self.assertRaises(ValueError, code_reorder.is_correct, None, '')

    def test_default_incorrect(self):
        answer = [
'''for (int i=1; i<20; i+=1) {
line(i*10, i*10, i*10, 190);
}''',
'''rect(30,40,50,50);''',
'''rect(20,20,40,40);''',
'''ellipse(56, 46, 55, 55);''',
'''if (number < 35) {''',
'''}''',
'''else if (number > 50) {''',
'''}''',
'''else {''',
'''}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))

    def test_incorrect(self):
        answer = [
'''if (number < 35) {''',
'''rect(30,40,50,50);''',
'''rect(20,20,40,40);''',
'''}''',
'''else if (number > 50) {''',
'''for (int i=1; i<20; i+=1) {
line(i*10, i*10, i*10, 190);
}''',
'''}''',
'''else {''',
'''ellipse(56, 46, 55, 55);''',
'''}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))

    def test_incomplete(self):
        answer = [
'''if (number < 35) {''',
'''rect(20,20,40,40);''',
'''rect(30,40,50,50);''',
'''}''',
'''else if (number > 50) {''',
'''for (int i=1; i<20; i+=1) {
line(i*10, i*10, i*10, 190);
}''',
'''else {''',
'''ellipse(56, 46, 55, 55);''',
'''}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))


class TestGradingCorrect(unittest.TestCase):

    def test_correct(self):
        answer = [
'''if (number < 35) {''',
'''rect(20,20,40,40);''',
'''rect(30,40,50,50);''',
'''}''',
'''else if (number > 50) {''',
'''for (int i=1; i<20; i+=1) {
line(i*10, i*10, i*10, 190);
}''',
'''}''',
'''else {''',
'''ellipse(56, 46, 55, 55);''',
'''}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertTrue(code_reorder.is_correct(None, state))
