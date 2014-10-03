"""
Django settings for gallery app.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

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

ENVIRONMENT = "preview"

if ENVIRONMENT == 'staging':

    DATABASES = {
        'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'processingjs_gallery_staging',
             'USER': 'gallery_rw',
             'PASSWORD': 'gAll3rY-rw',
        }
    }
    STATIC_URL = '/staging/static/'
    ALLOWED_HOSTS = [
        'loco.services.adelaide.edu.au',
    ]

elif ENVIRONMENT == 'preview':

    TEMPLATE_DEBUG = True
    DATABASES = {
        'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'processingjs_gallery_preview',
             'USER': 'gallery_rw',
             'PASSWORD': 'gAll3rY-rw',
        }
    }
    STATIC_URL = '/processingjs/static/'
    ALLOWED_HOSTS = [
        'loco.services.adelaide.edu.au',
    ]

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


# else - no database defined



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
    'artwork',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'gallery.urls'

WSGI_APPLICATION = 'gallery.wsgi.application'


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


# Authentication
LOGIN_URL = 'django.contrib.auth.views.login'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Django's default auth backend
    'rulez.backends.ObjectPermissionBackend',
]
