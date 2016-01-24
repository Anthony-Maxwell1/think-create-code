import sys
import os.path

python='./.virtualenv/bin/python'
pythonpath='./.virtualenv/lib/python2.7/site-packages/:./processingjs'
data_dir = os.path.join('redirect', 'data')
manage_py = os.path.join('processingjs', 'manage.py')

def get_app_env(target=False):
    if len(sys.argv) < 2:
        print "Usage %s <source_env>" % sys.argv[0]
        sys.exit(1)
    source = sys.argv[1]

    if target:
        if len(sys.argv) < 3:
            print "Usage %s <source_env> <target_env>" % sys.argv[0]
            sys.exit(1)
        target = sys.argv[2]
        return (source, target)

    return source

def get_data_dir(app_env):
    return os.path.join(data_dir, app_env)

def get_data_filename(app_env, model):
    return os.path.join(get_data_dir(app_env), '%s.json' % model)

models=[
    "database_files.file",
    "lti.user",
    "artwork.artwork",
    "exhibitions.exhibition",
    "submissions.submission",
    "votes.vote",
]

model_fields={
    "database_files.file": {
    },
    "lti.user": {
        'cohort': '_cohort_',
        'groups': None,
        'user_permissions': None,
    },
    "artwork.artwork": {
        'author': 'lti.user',
    },
    "exhibitions.exhibition": {
        'cohort': '_cohort_',
        'author': 'lti.user',
        'image': 'database_files.file',
    },
    "submissions.submission": {
        'artwork': 'artwork.artwork',    
        'exhibition': 'exhibitions.exhibition',    
        'submitted_by': 'lti.user',
        'score': None,
    },
    "votes.vote": {
        'voted_by': 'lti.user',
        'submission': 'submissions.submission',    
    },
}
