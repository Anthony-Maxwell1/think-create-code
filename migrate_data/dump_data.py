#!/bin/env python
import sys
sys.path.append('.')

import subprocess
from migrate_data.env import get_app_env, get_data_dir, get_data_filename, python, pythonpath, manage_py, models

app_env = get_app_env()
env = {
    'DJANGO_GALLERY_ENVIRONMENT': app_env,
    'PYTHONPATH': pythonpath,
}
subprocess.call(['mkdir', '-p', get_data_dir(app_env)])
for model in models:
    filename = get_data_filename(app_env, model)
    print "dumping %s to %s" % (model, filename)
    output = open(filename, 'w')
    subprocess.Popen([python, manage_py, 'dumpdata', '--indent', '2', model], env=env, stdout=output)
    output.close()
