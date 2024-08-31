config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default'
        }
    },
    'loggers': {
        '__main__': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'src.rpc_server': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'src.clients.rpc': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'src.rpc_config': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'src.wallet': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'src.subscription': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'src.view.history': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
}