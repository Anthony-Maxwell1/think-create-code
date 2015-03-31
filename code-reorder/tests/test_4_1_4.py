# -*- coding: utf-8 -*-
'''

USAGE:
    python -m unittest tests.test_4_1_4

    coverage run --include=./*.py  -m unittest tests.test_4_1_4
'''
import unittest
import json

import code_reorder_4_1_4 as code_reorder


class TestGradingIncorrect(unittest.TestCase):

    def test_incorrect_empty(self):
        self.assertRaises(ValueError, code_reorder.is_correct, None, '')

    def test_default_incorrect(self):
        answer = [
'''ellipse(50, 50, 30, 30);
}''',
'''rect(10, 10, 100, 100);
}''',
'''if (test == 10) {''',
'''else {''',
'''size(200, 200);
int test = 10;''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))

    def test_incorrect(self):
        answer = [
'''size(200, 200);
int test = 10;''',
'''if (test == 10) {''',
'''ellipse(50, 50, 30, 30);
}''',
'''else {''',
'''rect(10, 10, 100, 100);
}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))

    def test_incomplete(self):
        answer = [
'''if (test == 10) {''',
'''rect(10, 10, 100, 100);
}''',
'''else {''',
'''ellipse(50, 50, 30, 30);
}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))


class TestGradingCorrect(unittest.TestCase):

    def test_correct(self):
        answer = [
'''size(200, 200);
int test = 10;''',
'''if (test == 10) {''',
'''rect(10, 10, 100, 100);
}''',
'''else {''',
'''ellipse(50, 50, 30, 30);
}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertTrue(code_reorder.is_correct(None, state))
