import re

from .base import *

LOGGING['loggers'][''] = {
    'handlers': ['log_to_stdout'],
    'level': 'DEBUG',
    'propagate': True,
}
import logging.config
logging.config.dictConfig(LOGGING)

DEBUG = TEMPLATE_DEBUG = True

# Send emails to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# or, use GMail
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'USERNAME@gmail.com'
#EMAIL_HOST_PASSWORD = 'PASSWORD'

DEBUG_APPS = (
    'debug_toolbar',
    'django_extensions',
    'django_jenkins'
)
INTERNAL_IPS = ('127.0.0.1',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)


# Don't show DDT in the admin
def show_toolbar(request):
    uri = request.get_full_path()
    if re.match(r'/admin/', uri):
        return False
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': "sparrow.settings.local.show_toolbar",
}

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes'
)

INSTALLED_APPS += DEBUG_APPS
