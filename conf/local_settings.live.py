import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

# is the live environment after all
DEBUG = False

ADMINS = (
    ('Ross Crawford-d\'Heureuse', 'ross.crawford@adcloud.com'),
)

SITE_ID = 2 # as per c9_sites.json fixtures

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_DIR, '../data/dev.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# setup for webfaction paths
MEDIA_ROOT = os.path.join(PROJECT_DIR, '../../media/people')
STATIC_ROOT = os.path.join(PROJECT_DIR, '../../static/people')
