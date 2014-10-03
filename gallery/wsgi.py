"""
WSGI config for gallery app.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

# Append the app base path and virtualenv dirs in the python path
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, '../', '.virtualenv'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gallery.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
