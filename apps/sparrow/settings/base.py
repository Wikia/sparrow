# Base settings file

import os
import sys
from unipath import Path

from django.core.exceptions import ImproperlyConfigured

import dj_database_url

PROJECT_ROOT = Path(__file__).ancestor(4)


def get_env_var(varname, default=None):
    """Get the environment variable or raise an exception."""
    try:
        return os.environ[varname]
    except KeyError:
        if default is not None:
            return default
        msg = "You must set the {0} environment variable.".format(varname)
        raise ImproperlyConfigured(msg)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': dj_database_url.parse(get_env_var('SPARROW_DATABASE_URL'))
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = PROJECT_ROOT.child('static').child('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = PROJECT_ROOT.child('static').child('_build')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = ()

# Make this unique, and don't share it with anybody.
SECRET_KEY = get_env_var('SPARROW_SECRET_KEY')

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'sparrow.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sparrow.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PROJECT_ROOT.child('templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = (
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',

    # local apps
    'rest_framework_swagger',
    'test_runs',
    'results',
    'tasks',
    'testrunner',
    'metrics',
)

# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'PAGE_SIZE': 10
}

ACCOUNT_ACTIVATION_DAYS = 7

# Celery Settings
BROKER_URL = get_env_var('SPARROW_CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'redis'
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# AUTH_USER_MODEL = 'path.to.UserModel'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

# see: https://www.caktusgroup.com/blog/2015/01/27/Django-Logging-Configuration-logging_config-default-settings-logger/
LOGGING_CONFIG = None

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'log_to_stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'testrunner': {
            'handlers': ['log_to_stdout'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s"
        }
    }
}

import logging.config
logging.config.dictConfig(LOGGING)

SPARROW_TEST_RUNNER = {
    'deploy_host': {
        'hostname': get_env_var('SPARROW_RUNNER_DEPLOY_HOST'),
    },
    'target_hosts': [
        {
            'hostname': get_env_var('SPARROW_RUNNER_TARGET_HOST'),
        }
    ],
    'api_server': get_env_var('SPARROW_API_URI'),
}
