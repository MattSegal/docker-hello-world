from . import *

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = [
	'www.redditfeed.xyz',
	'redditfeed.xyz',
    '167.99.78.141',
    '127.0.0.1',
    'localhost',
]

# Logging
LOGGING['root']['handlers'] = ['console', 'sentry']
LOGGING['handlers']['sentry'] = {
    'level': 'ERROR',
    'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
}

RAVEN_CONFIG = {
    'dsn': os.environ.get('REDDIT_RAVEN_DSN')
}
