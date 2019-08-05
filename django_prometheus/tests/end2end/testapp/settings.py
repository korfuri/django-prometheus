import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", __file__)

import django
django.setup()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')0-t%mc5y1^fn8e7i**^^v166@5iu(&-2%9#kxud0&4ap#k!_k'

# SECURITY WARNING: don't run with debug turned on in production!
#
# BIGGER SECURITY WARNING: if you're trying to disable DEBUG, you're
# probably trying to run the testapp in production. DO NOT RUN THE
# TESTAPP IN PRODUCTION. It contains several features that are
# horrible hacks or even intentional security holes, to facilitate
# automated or manual testing (like /sql which lets you, or anyone,
# execute arbitrary SQL queries). DO NOT RUN THE TESTAPP IN
# PRODUCTION.
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_prometheus',
    'testapp',
)


def GetMiddlewareClasses():
    classes = ['django_prometheus.middleware.PrometheusBeforeMiddleware']
    classes.extend([
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware'])
    if django.VERSION < (1, 10):
        classes.append(
            'django.contrib.auth.middleware.SessionAuthenticationMiddleware')
    classes.extend([
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware'])
    classes.append('django.middleware.security.SecurityMiddleware')
    classes.append('django_prometheus.middleware.PrometheusAfterMiddleware')
    return classes


# For Django 1.x
MIDDLEWARE_CLASSES = GetMiddlewareClasses()
# For Django 2.x
MIDDLEWARE = MIDDLEWARE_CLASSES

ROOT_URLCONF = 'testapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'testapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },

    # Comment this to not test django_prometheus.db.backends.postgres.
    'postgresql': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    },

    # Comment this to not test django_prometheus.db.backends.mysql.
    'mysql': {
        'ENGINE': 'django_prometheus.db.backends.mysql',
        'NAME': 'django_prometheus_1',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    },

    # The following databases are used by test_db.py only
    'test_db_1': {
        'ENGINE': 'django_prometheus.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test_db_1.sqlite3'),
    },
    'test_db_2': {
        'ENGINE': 'django_prometheus.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test_db_2.sqlite3'),
    },
}

# Caches

CACHES = {
    'default': {
        'BACKEND': 'django_prometheus.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
    },
    'memcached': {
        'BACKEND': 'django_prometheus.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
    },
    'filebased': {
        'BACKEND': 'django_prometheus.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    },
    'locmem': {
        'BACKEND': 'django_prometheus.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/locmem_cache',
    },
    'redis': {
        'BACKEND': 'django_prometheus.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    },
    # Fake redis config emulated stopped service
    'stopped_redis': {
        'BACKEND': 'django_prometheus.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6666/1',
    },
    'stopped_redis_ignore_exception': {
        'BACKEND': 'django_prometheus.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6666/1',
        "OPTIONS": {
            "IGNORE_EXCEPTIONS": True,
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# django_prometheus name
DJANGO_PROMETHEUS_NAME = 'test_app'
