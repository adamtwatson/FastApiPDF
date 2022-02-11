from logging import config

LOG_LEVEL = 'DEBUG'
LOG_NAME = 'FastApiPDF'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(pathname)s:%(lineno)s] %(message)s',
        },
    },
    'filters': {
        # 'special': {
        #     '()': 'project.logging.SpecialFilter',
        #     'foo': 'bar',
        # }
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        LOG_NAME: {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            # 'filters': ['special']
        }
    }
}

config.dictConfig(LOGGING)
