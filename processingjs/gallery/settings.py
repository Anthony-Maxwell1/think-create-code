"""
Django settings for gallery app.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm=2w&k4)f^1-ii04p(b88%_&%$w!(s)p)%gqvh@ac498566p+s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

# Determine enviroment to run in
if 'test' in sys.argv:
    ENVIRONMENT = "testing"
elif 'runserver' in sys.argv:
    ENVIRONMENT = "development"
else:
    #FIXME ENVIRONMENT = "production"
    ENVIRONMENT = "lti-test"


if ENVIRONMENT == 'production':

    DATABASES = {
        'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'processingjs_gallery',
             'USER': 'gallery_rw',
             'PASSWORD': 'gAll3rY-rw',
        }
    }
    STATIC_URL = '/Think.Create.Code/static/'
    ALLOWED_HOSTS = ['*']

elif ENVIRONMENT == 'lti-test':

    DATABASES = {
        'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'processingjs_lti_gallery',
             'USER': 'gallery_rw',
             'PASSWORD': 'gAll3rY-rw',
        }
    }
    STATIC_URL = '/Think.Create.Code/static/'
    ALLOWED_HOSTS = ['*']

    DEBUG = True
    TEMPLATE_DEBUG = True

elif ENVIRONMENT == 'development':

    # Runs via ./manage.py runserver
    DEBUG = True
    TEMPLATE_DEBUG = True
    DATABASES = {
        'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'processingjs_gallery_dev',
             'USER': 'gallery_rw',
             'PASSWORD': 'gAll3rY-rw',
        }
    }
    STATIC_URL = '/static/'
    ALLOWED_HOSTS = []

elif ENVIRONMENT == 'testing':

    # Runs via ./manage.py test
    DEBUG = False
    TEMPLATE_DEBUG = False
    DATABASES = {
        'default': {
             'ENGINE': 'django.db.backends.sqlite3',
             'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
        }
    }
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    ALLOWED_HOSTS = ['localhost']


# else - error: no database defined



# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rulez',
    'uofa',
    'artwork',
    'exhibitions',
    'submissions',
    'votes',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'harvard.django_auth_lti.middleware.LTIAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'gallery.urls'

WSGI_APPLICATION = 'gallery.wsgi.application'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join( BASE_DIR, 'static' ),
)


TEMPLATE_DIRS = (
    os.path.join( BASE_DIR, 'templates' ),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

# Authentication
LOGIN_URL = 'django.contrib.auth.views.login'
LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Django's default auth backend
    'harvard.django_auth_lti.backends.LTIAuthBackend',
    'rulez.backends.ObjectPermissionBackend',
]

AUTH_USER_MODEL = 'uofa.User'

# FIXME - how to manage security?
LTI_OAUTH_CREDENTIALS = {
    'test': 'uoa_secret',
    'test2': 'uoa_reallysecret',
}
