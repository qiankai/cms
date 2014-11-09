"""
Django settings for cmstodo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUGE = True

APPID = "wxa1dffce607b94e53"
APPSECRET = "8e03f24f449405171fc0dbf94fd29622"

SITE_URL = "http://3.ithinks.sinaapp.com/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qg(3=uo(mx(@6t7*oebswb=rt)#^a9(ibmn68)0(wy%_p$mzec'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DIRS=( os.path.join(BASE_DIR,'templates'),)

STATIC_ROOT = os.path.join(BASE_DIR,'static')

STATIC_DIRS = ( os.path.join(BASE_DIR,'static'),)

STATIC_URL = '/static/'

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []



# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'authserver',
    'usernet',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
)


ROOT_URLCONF = 'cmstodo.urls'

WSGI_APPLICATION = 'cmstodo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

if 'SERVER_SOFTWARE' in os.environ:
   from sae.const import (
       MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB
   )
else:
   MYSQL_HOST = 'localhost'
   MYSQL_PORT = '3306'
   MYSQL_USER = 'root'
   MYSQL_PASS = 'root'
   MYSQL_DB   = 'app_pylabs'
DATABASES = {
   'default': {
       'ENGINE':   'django.db.backends.mysql',
       'NAME':     MYSQL_DB,
       'USER':     MYSQL_USER,
       'PASSWORD': MYSQL_PASS,
       'HOST':     MYSQL_HOST,
       'PORT':     MYSQL_PORT,
   }
}


WECHAT_TOKEN = 'presalecci'
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


