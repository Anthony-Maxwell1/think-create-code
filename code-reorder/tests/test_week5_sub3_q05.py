# -*- coding: utf-8 -*-
'''

USAGE:
    python -m unittest tests.test_week5_sub3_q05

    coverage run --include=./*.py  -m unittest tests.test_week5_sub3_q05
'''
import unittest
import json

import code_reorder_week5_sub3_q05 as code_reorder


class TestGradingIncorrect(unittest.TestCase):

    def test_incorrect_empty(self):
        self.assertRaises(ValueError, code_reorder.is_correct, None, '')

    def test_default_incorrect(self):
        answer = ['''size(200,200);
background(140,40,40);''',
'''rotate(PI/18);''',
'''rect(0,0,100,20);''',
'''for (int i=0; i<10; i++) {''',
'''}''',
'''translate(50,50);''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))

    def test_incorrect(self):
        answer = ['''size(200,200);
background(140,40,40);''',
'''rect(0,0,100,20);''',
'''for (int i=0; i<10; i++) {''',
'''rotate(PI/18);''',
'''}''',
'''translate(50,50);''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))

    def test_incomplete(self):
        answer = ['''size(200,200);
background(140,40,40);''',
'''rect(0,0,100,20);''',
'''for (int i=0; i<10; i++) {''',
'''}''',
'''translate(50,50);''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))


class TestGradingCorrect(unittest.TestCase):

    def test_correct(self):
        answer = [
'''size(200,200);
background(140,40,40);''',
'''translate(50,50);''',
'''for (int i=0; i<10; i++) {''',
'''rect(0,0,100,20);''',
'''rotate(PI/18);''',
'''}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertTrue(code_reorder.is_correct(None, state))
