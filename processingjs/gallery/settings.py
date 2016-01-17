"""
Django settings for gallery app.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Note: environment-specific and sensitive settings are in gallery/env/*.ini
from ConfigParser import RawConfigParser
from string import upper
env_config = RawConfigParser()
env_config.optionxform = upper # make options uppercase (default is lowercase)
env_config.read(os.path.join(BASE_DIR, 'env', 'default.ini'))

# Determine enviroment we're running in
ENVIRONMENT = os.environ.get("DJANGO_GALLERY_ENVIRONMENT", env_config.get('GENERAL', 'ENVIRONMENT'))
# Put env-specific config in .ini file.  Ignored if file does not exist.
env_config.read(os.path.join(BASE_DIR, 'env', '%s.ini' % ENVIRONMENT))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env_config.get('GENERAL', 'SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_config.getboolean('GENERAL', 'DEBUG')

# Configure logging
import logging
from logging import config as logging_config
LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, env_config.get('GENERAL', 'LOGGING_CONFIG_FILE'))
logging_config.fileConfig(LOGGING_CONFIG_FILE)

DATABASES = {
    'default': dict(env_config.items('DATABASE'))
}
STATIC_URL = env_config.get('GENERAL', 'STATIC_URL')
ALLOWED_HOSTS = env_config.get('GENERAL', 'ALLOWED_HOSTS').split()

SHARE_URL = env_config.get('GALLERY', 'SHARE_URL')
ALLOW_ANALYTICS = env_config.getboolean('GALLERY', 'ALLOW_ANALYTICS')

ARTWORK_CSP_SCRIPT_SRC = env_config.get('ARTWORK', 'CSP_SCRIPT_SRC').split()
ARTWORK_CSP_STYLE_SRC = env_config.get('ARTWORK', 'CSP_STYLE_SRC').split()

# LTI settings
ADELAIDEX_LTI = dict(env_config.items('ADELAIDEX_LTI'))
ADELAIDEX_LTI['COURSE_URL'] = ADELAIDEX_LTI.get('LOGIN_URL', None)
if 'OAUTH_KEY' in ADELAIDEX_LTI and 'OAUTH_SECRET' in ADELAIDEX_LTI:
    LTI_OAUTH_CREDENTIALS = {
        ADELAIDEX_LTI.get('OAUTH_KEY') : ADELAIDEX_LTI.get('OAUTH_SECRET')
    }

# Disqus integration
ADELAIDEX_LTI_DISQUS = dict(env_config.items('ADELAIDEX_LTI_DISQUS'))

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rulez',
    'database_files',
    'gallery',
    'django_adelaidex.util',
    'django_adelaidex.lti',
    'artwork',
    'exhibitions',
    'submissions',
    'votes',
)

MIDDLEWARE_CLASSES = (
    'django_adelaidex.util.middleware.WsgiLogErrors',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_auth_lti.middleware.LTIAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'csp.middleware.CSPMiddleware',
    'django_adelaidex.util.middleware.P3PMiddleware',
    'django_adelaidex.lti.middleware.TimezoneMiddleware',
)

ROOT_URLCONF = 'gallery.urls'

WSGI_APPLICATION = 'gallery.wsgi.application'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEFAULT_FILE_STORAGE = 'database_files.storage.DatabaseStorage'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join( BASE_DIR, 'static' ),
)

# Note: used only during testing.
# In production, we simply serve the static dir as-is.
STATIC_ROOT = os.path.join( BASE_DIR, 'static', 'test' )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
                'django_adelaidex.util.context_processors.analytics',
                'django_adelaidex.util.context_processors.referer',
                'django_adelaidex.util.context_processors.base_url',
                'django_adelaidex.lti.context_processors.lti_settings',
                'django_adelaidex.lti.context_processors.disqus_settings',
                'django_adelaidex.lti.context_processors.disqus_sso',
            ],
        },
    },
]

# P3P header
P3P_HEADER_KEY = 'P3P:CP'
P3P_HEADER_VALUE = 'IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT'

# Content Security Policy
CSP_DEFAULT_SRC = (
    "'self'",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'", # artwork/_render.html, artwork/edit.html
    "https://www.google-analytics.com",
) + tuple(ADELAIDEX_LTI_DISQUS.get('CSP_SCRIPT_SRC', '').split())
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https://www.google-analytics.com",
) + tuple(ADELAIDEX_LTI_DISQUS.get('CSP_IMG_SRC', '').split())
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'", # modernizr.js
) + tuple(ADELAIDEX_LTI_DISQUS.get('CSP_STYLE_SRC', '').split())
CSP_FRAME_SRC = (
    "'self'", 
) + tuple(ADELAIDEX_LTI_DISQUS.get('CSP_FRAME_SRC', '').split())


# Authentication
LOGIN_URL = 'login'

from django.core.urlresolvers import reverse_lazy
LOGIN_REDIRECT_URL = reverse_lazy('home')

AUTHENTICATION_BACKENDS = [
    'django_adelaidex.lti.backends.CohortLTIAuthBackend',
    'django.contrib.auth.backends.ModelBackend', # Django's default auth backend
    'rulez.backends.ObjectPermissionBackend',
]

AUTH_USER_MODEL = 'lti.User'

ADELAIDEX_LTI_STAFF_MEMBER_GROUP = 1
