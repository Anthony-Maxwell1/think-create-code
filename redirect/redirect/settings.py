
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY='k)y1i_k$$**5n#0iibwg^1h$oj)d(s1351-2%k(4&f)==7sd9t'

# Configure logging
import logging
from logging import config as logging_config
LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, 'logging.conf')
logging_config.fileConfig(LOGGING_CONFIG_FILE)

ROOT_URLCONF = 'redirect.urls'
WSGI_APPLICATION = 'redirect.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'redirect',
)

ALLOWED_HOSTS = '*'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REDIRECT_MAP = {
    '/': # testing, https://bit.ly/1A3JLXA
        os.path.join(BASE_DIR, 'data', 'production-2T2015'),
    '/think.create.code/gallery/': # https://bit.ly/1A3Kdoy
        os.path.join(BASE_DIR, 'data', 'production-2T2015'),
    '/think.create.code/3t2015/gallery/': # https://bit.ly/1JjomIB
        os.path.join(BASE_DIR, 'data', 'production-3T2015'),
}

REDIRECT_BASE = 'https://lti-adx.adelaide.edu.au/think.create.code/processingjs'
