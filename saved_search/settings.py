import djcelery

from default_settings import *
from secrets import STAGING_DB_PASSWD

"""
Settings for staging web servers
"""

djcelery.setup_loader()

DATABASES = {
    'default': {
        'NAME': 'directseo',
        'ENGINE': 'mysql',
        'USER': 'db_deuser',
        'PASSWORD': STAGING_DB_PASSWD,
        'HOST': 'db-directseo-staging.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': '3306'
    },
}

TEMPLATE_DIRS = (
    '/home/web/direct-seo/directseo/templates/',
)

# cause we dont want people seeing important environment info on an error
DEBUG = True

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

CELERY_ALWAYS_EAGER = True

HAYSTACK_SOLR_URL = 'http://184.73.212.114/solr'
