# -*- coding: utf-8 -*-
''' 
To be wrapped inside a Custom javascript problem, with a corresponding html
file, which defines the JS functions.

E.g.,

<problem display_name="week3_sec3_q7">
   <script type="loncapa/python">
   <![CDATA[
        # def is_correct(...) code goes here
   ]]>
   </script>
   <customresponse cfn="is_correct">
       <jsinput
           height="1100"
           width="600"
           gradefn="CodeReorder.get_grade"
           get_statefn="CodeReorder.get_state"
           set_statefn="CodeReorder.set_state"
           html_file="/static/code_reorder_3_3_7.html" />
   </customresponse>
</problem>
'''

EXPECTED = [
'''
size(250, 250);
int red = 220;
int blue = 180;
int green = 100;
int extra = 10;
int x = 20;''',
'''
for (int counter=1; counter<=5; counter = counter + 1) {''',
'''
    green = 100;
    extra = x;''',
'''
    for (int y=100; y>=20; y= y - 20) {''',
'''
        green = green + 35;
        fill(red, green, blue);''',
'''
        ellipse(extra, y, 20, 20);''',
'''
        extra = extra+20;''',
'''
    }
    x = x + 20;
}''',
]

import json
import re

# Strip leading and trailing spaces
def wsstrip(string):
    lines = string.splitlines()
    for i in range(0, len(lines)):
        lines[i] = lines[i].strip()
        # Remove spaces around operators and punctuation, to guard against typos.
        lines[i] = re.sub(r'\s*([=<>+;,\/\.*-]+)\s*', r'\1', lines[i])
    return ''.join(lines)

def is_correct(exp, given):

    # The 'given' string is parsed into "answer" and "state" JSON strings
    # parsed['answer'] = the return value of the configured JS gradefn
    # parsed['state']  = the return value of the configured JS get_statefn
    #
    # We only use 'state', because the other seems redundant.

    parsed = json.loads(given)
    state = parsed.get('state', '{}')
    state = json.loads(state)
    answer = state.get('code', '[]')
    if len(answer) and len(answer) == len(EXPECTED):
        for i in range(len(EXPECTED)):
            exp = wsstrip(EXPECTED[i])
            ans = wsstrip(answer[i])
            if exp != ans:
                return False
        return True

    return False
