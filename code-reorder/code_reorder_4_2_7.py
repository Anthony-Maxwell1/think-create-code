# -*- coding: utf-8 -*-
''' 
To be wrapped inside a Custom javascript problem, with a corresponding html
file, which defines the JS functions.

E.g.,

<problem display_name="week4_sec2_q7">
   <script type="loncapa/python">
   <![CDATA[
        # def is_correct(...) code goes here
   ]]>
   </script>
   <customresponse cfn="is_correct">
       <jsinput
           height="1550"
           width="600"
           gradefn="CodeReorder.get_grade"
           get_statefn="CodeReorder.get_state"
           set_statefn="CodeReorder.set_state"
           html_file="/static/code_reorder_4_2_7.html" />
   </customresponse>
</problem>
'''

EXPECTED = [
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
