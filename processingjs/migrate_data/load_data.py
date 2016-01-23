#!/bin/env python
from migrate_data.env import get_app_env, get_data_filename, pythonpath, models, model_fields
import os
import re
import sys
import json
import copy
import datetime

sys.path.append(pythonpath)
(source_env, target_env) = get_app_env(target=True)
os.environ['DJANGO_SETTINGS_MODULE'] = 'gallery.settings'
os.environ['DJANGO_GALLERY_ENVIRONMENT'] = target_env

import django
django.setup()

from django.apps import apps
from django.db import connection
from django.utils.crypto import get_random_string
from django_adelaidex.lti.models import User, Cohort

# Get or create cohort
try:
    cohort = Cohort.objects.get(oauth_key=source_env)
    created = False
except Cohort.DoesNotExist:
    oauth_secret = get_random_string(50,'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
    cohort = Cohort.objects.create(
        title = source_env,
        oauth_key=source_env, 
        oauth_secret=oauth_secret,
    )
    created = True

if created:
    print "Created cohort for %s" % source_env
else:
    print "Found cohort for %s" % source_env

# Get or create cuid:student user
try:
    edge_user = User.objects.get(username="cuid:student")
    created = False
except User.DoesNotExist:
    edge_user = User.objects.create(
      cohort=None,
      username="cuid:student", 
      first_name="edge-instructor", 
      last_name="", 
      is_active=True, 
      time_zone="Australia/Adelaide", 
      is_superuser=False, 
      is_staff=True, 
      last_login="2015-10-02T01:10:17Z", 
      password="", 
      email="jill.vogel@adelaide.edu.au", 
      date_joined="2015-07-20T00:27:55Z"
    )
    created = True

if created:
    print "Created edge user for %s" % source_env
else:
    print "Found edge user for %s" % source_env


pk_map = {}
file_re = re.compile('^(?P<prefix>\D*)(?P<pk>\d+)(?P<suffix>.*)$')
error_objs = []

for name in models:
#for name in ['lti.user', 'artwork.artwork', 'exhibitions.exhibition', 'submissions.submission', 'votes.vote']:
    (app_label, model_name) = name.split('.')
    model = apps.get_model(app_label, model_name)
    if model.objects.count():
        last_obj = model.objects.latest('id')
        next_id = last_obj.id + 1
    else:
        next_id = 1

    # Read JSON data file
    filename = get_data_filename(source_env, name)
    print "Reading %s from %s" % (name, filename)
    input_file = open(filename, 'r')
    input_objs = json.load(input_file)
    input_file.close()

    print "load %s %s objs, starting at %s" % (len(input_objs), name, next_id)
    pk_map[name] = {}
    for obj in input_objs:
        fields = copy.copy(obj['fields'])
        mfields = model_fields.get(name, {})

        try:
            if (name == 'lti.user') and (fields.get('username', '') == edge_user.username):
                new_obj = edge_user
            else:
                for (field, fmodel) in mfields.iteritems():
                    #print "assessing %s: %s" % (field, fmodel)

                    # Remove indicated fields
                    if fmodel is None:
                        #print "removed %s" % field
                        del fields[field]

                    # Set cohort
                    elif fmodel == '_cohort_':
                        #print "set cohort"
                        fields[field] = cohort
                    else:
                        #print "set foreign key"

                        # Load pk map from file if not found
                        if not fmodel in pk_map:
                            filename = get_data_filename(source_env, '%s.map' % fmodel)
                            print "Reading %s pk map from %s" % (fmodel, filename)
                            map_file = open(filename, 'r')
                            pk_map[fmodel] = json.load(map_file)
                            map_file.close()

                        # database files are special
                        if fmodel == 'database_files.file':
                            old_img = fields[field]
                            match = file_re.search(old_img)
                            old_pk = match.group('pk')
                            new_pk = pk_map[fmodel][str(old_pk)]
                            fields[field] = '%s%s%s' % (match.group('prefix'), new_pk, match.group('suffix'))
                        # all other fields are foreign keys
                        else:
                            old_pk = fields[field]
                            new_pk = pk_map[fmodel][str(old_pk)]
                            del fields[field]
                            fields['%s_id'%field] = new_pk

                #print "Creating %s from (%s)" % (name, fields)
                new_obj = model.objects.create(**fields)

                # Force update the date fields
                if ('created_at' in fields) and ('modified_at' in fields):
                    date_format = '%Y-%m-%dT%TZ'
                    sql = "UPDATE %s SET created_at=str_to_date('%s','%s'), modified_at=str_to_date('%s','%s') WHERE id=%s" % ( 
                        new_obj._meta.db_table,
                        fields['created_at'], date_format,
                        fields['modified_at'], date_format,
                        new_obj.id,
                    )
                    cursor = connection.cursor()
                    cursor.execute(sql)

            pk_map[name][str(obj['pk'])] = new_obj.id

        except Exception as e:
            obj['exception'] = str(e)
            error_objs.append(obj)

    filename = get_data_filename(source_env, '%s.map' % name)
    map_file = open(filename, 'w')
    json.dump(pk_map[name], map_file, indent=2)
    map_file.close()

if error_objs:
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = get_data_filename(source_env, timestamp)
    print "%s errors, storing to %s" % (len(error_objs), filename)
    err_file = open(filename, 'w')
    json.dump(error_objs, err_file, indent=2)
    err_file.close()
