#!/bin/env python
import subprocess
from migrate_data.env import get_app_env, get_data_filename, python, pythonpath, models

app_env = get_app_env()
env = {
    'DJANGO_GALLERY_ENVIRONMENT': app_env,
    'PYTHONPATH': pythonpath,
}
subprocess.call(['mkdir', '-p', app_env])
for model in models:
    filename = get_data_filename(app_env, model)
    print "dumping %s to %s" % (model, filename)
    output = open(filename, 'w')
    subprocess.Popen([python, 'manage.py', 'dumpdata', '--indent', '2', model], env=env, stdout=output)
    output.close()
