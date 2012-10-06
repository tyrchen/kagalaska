# Django settings for kagalaska project.
import os

# Tag APP
PROJECT_HOME = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
TMP_HOME = '/tmp/'
DATA_PATH = os.path.join(PROJECT_HOME, 'tag', 'data')

# DATA PATH
WORDS_PATH = os.path.join(DATA_PATH, 'words.dic')
CHARS_PATH = os.path.join(DATA_PATH, 'chars.dic')
RELATIONS_PATH = os.path.join(DATA_PATH, 'relations')
TRAIN_RATE_PATH = os.path.join(DATA_PATH, 'tag_rate_train.dic')
WORDS_RATE_PATH = os.path.join(DATA_PATH, 'words_rate.dic')
TAG_TO_FILE_PATH = os.path.join(DATA_PATH, 'tag_words.dic')
TAGS_RESOURCE_PATH = os.path.join(DATA_PATH, 'tags_source.csv')

#UNIX_DOMAIN
WORDSEG_UNIX_DOMAIN = os.path.join(TMP_HOME, 'wordseg.sock')
RELATIONS_UNIX_DOMAIN = os.path.join(TMP_HOME, 'relations.sock')
PLACEINFO_UNIX_DOMAIN = os.path.join(TMP_HOME, 'place_info.sock')

#MONGO_DB
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'kagalaska'

# DEFAULTS
NEW_WORD_DEFAULT_VALUE = 1.0 # any tag added, the score is 1.0
TITLE_WEIGHT = 2.0 # weight of title
CONTENT_WEIGHT = 1.0 # weight of content
FILTER_THRESHOLD = 0.03 # tags score gt 0.03 will be available
TOP_N = 3 # return 3 top places and 3 normal tags.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r39vbv(p0=khthi#+j)=0#p-mvyo%v!0xzzt2giq7db@%^jc1n'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'kagalaska.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'kagalaska.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'tag'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
#LOGGER
MY_LOG_FILENAME = os.path.join(PROJECT_HOME, 'logs', 'kagalaska.log')

LOGGING = {
  'version': 1,
  'formatters': {
    'verbose': {
      'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    },
      'simple': {
      'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
    },
  },
  'handlers': {
    'rotating_file':{
      'level' : 'INFO',
        'formatter' : 'simple', # from the django doc example
        'class' : 'logging.handlers.TimedRotatingFileHandler',
        'filename' :   MY_LOG_FILENAME, # full path works
        'when' : 'midnight',
        'interval' : 1,
        'backupCount' : 7,
    },
  },
  'loggers': {
    '': {
    'handlers': ['rotating_file'],
    'level': 'INFO',
      }
    }
}