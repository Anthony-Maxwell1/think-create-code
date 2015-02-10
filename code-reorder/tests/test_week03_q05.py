# -*- coding: utf-8 -*-
'''

USAGE:
    python -m unittest tests.test_week03_q05

    coverage run --include=./*.py  -m unittest tests.test_week03_q05
'''
import unittest
import json

import code_reorder_week03_q05 as code_reorder


class TestGradingIncorrect(unittest.TestCase):

    def test_incorrect_empty(self):
        self.assertRaises(ValueError, code_reorder.is_correct, None, '')

    def test_default_incorrect(self):
        answer = ['''    green = 100;
    extra = x;
''', 
            '''    for (int y=100; y>=20; y= y - 20) {''', 
            '''size(250, 250);
int red=220;
int blue=180;
int green = 100;
int extra = 10;
int x = 20;
''', 
            '''for (int counter = 1; counter <=5; counter = counter + 1) {''',
            '''        extra = extra+20;''',
            '''        ellipse(extra, y, 20, 20);''',
            '''        green = green + 35;
        fill(red, green, blue);
''',
            '''    }
    x = x + 20;
}''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))

    def test_incorrect(self):
        answer = [
            '''for (int counter = 1; 
        counter <=5; 
        counter = counter + 1) {''',
            '''    green = 100;
        extra = x;''',
            '''    for (int y=100; y>=20; y= y - 20) {''',
            '''        green = green + 35;
            fill(red, green, blue);''',
            '''        ellipse(extra, y, 20, 20);''',
            '''        extra = extra+20;''',
            '''    }
        x = x + 20;
    }''',
            '''size(250, 250);
    int red=220;
    int blue=180;
    int green = 100;
    int extra = 10;
    int x = 20;''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))

    def test_incomplete(self):
        answer = [
            '''size(250, 250);
    int red=220;
    int blue=180;
    int green = 100;
    int extra = 10;
    int x = 20;''',
            '''for (int counter = 1; 
        counter <=5; 
        counter = counter + 1) {''',
            '''    green = 100;
        extra = x;''',
            '''    for (int y=100; y>=20; y= y - 20) {''',
            '''        green = green + 35;
            fill(red, green, blue);''',
            '''        ellipse(extra, y, 20, 20);''',
            '''        extra = extra+20;''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertFalse(code_reorder.is_correct(None, state))


class TestGradingCorrect(unittest.TestCase):

    def test_correct(self):
        answer = [
            '''size(250, 250);
    int red=220;
    int blue=180;
    int green = 100;
    int extra = 10;
    int x = 20;''',
            '''for (int counter=1; counter<=5; counter= counter + 1) {''',
            '''    green = 100;
        extra = x;''',
            '''    for (int y=100; y>=20; y= y - 20) {''',
            '''        green = green + 35;
            fill(red, green, blue);''',
            '''        ellipse(extra, y, 20, 20);''',
            '''        extra = extra+20;''',
            '''    }
        x = x + 20;
    }''',
        ]
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertTrue(code_reorder.is_correct(None, state))

    def test_submitted(self):
        answer = ['''size(250, 250);
int red=220;
int blue=180;
int green = 100;
int extra = 10;
int x = 20;
''', '''for (int counter= 1; counter<=5; counter= counter + 1) {''', '''    green = 100;
    extra = x;
''', '''    for (int y=100; y>=20; y= y - 20) {''', '''        green = green + 35;
        fill(red, green, blue);
''', '''        ellipse(extra, y, 20, 20);''', '''        extra = extra+20;''', '''    }
    x = x + 20;
}''']
        
        state = json.dumps({'state': json.dumps({'code': answer})})
        self.assertTrue(code_reorder.is_correct(None, state))
