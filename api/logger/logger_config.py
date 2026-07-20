import logging.config
import logging
import os

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
        'critical': {
            'format': '%(asctime)s [CRITICAL ERROR] %(filename)s:%(lineno)d - %(message)s'
        }
    },
    'handlers': {
        ################## BASE HANDLERS ##################
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/app.log',
            'level': 'INFO',
            'formatter': 'simple'
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
            'level': 'ERROR',
            'formatter': 'simple'
        },

        ################## CUSTOM HANDLERS ##################
        #---------- DB ----------
        'db_info': {
            'class': 'logging.FileHandler',
            'filename': 'logs/db.log',
            'level': 'INFO',
            'formatter': 'simple'
        },
        'db_error': {
            'class': 'logging.FileHandler',
            'filename': 'logs/db.log',
            'level': 'CRITICAL',
            'formatter': 'critical'
        }

    },
    'loggers': {
        'messenger.db': {
            'level': 'DEBUG',
            'handlers': ['db_info','db_error','console'],
            'propagate': False
        }
    },
    'root': {
        #'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger('root')