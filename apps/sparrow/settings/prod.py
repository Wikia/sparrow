from .base import *

LOGGING['loggers'][''] = {
    'handlers': ['log_to_stdout'],
    'level': 'WARNING',
    'propagate': True,
}
import logging.config
logging.config.dictConfig(LOGGING)
