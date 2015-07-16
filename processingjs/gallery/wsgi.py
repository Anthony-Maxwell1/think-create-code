"""
WSGI config for gallery app.

It exposes the WSGI callable as a module-level function named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

# Append the app base path and virtualenv dirs in the python path
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(BASE_DIR)
sys.path.insert(1, os.path.join(BASE_DIR, '../', '.virtualenv', 'lib', 'python2.7', 'site-packages'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gallery.settings")

# ref http://ericplumb.com/blog/passing-apache-environment-variables-to-django-via-mod_wsgi.html
def application(environ, start_response):
    # pass these WSGI environment variables on through to os.environ
    for var in ['DJANGO_GALLERY_ENVIRONMENT']:
        if var in environ:
            os.environ[var] = environ[var]

    from django.core.wsgi import get_wsgi_application
    _application = get_wsgi_application()
    return _application(environ, start_response)
