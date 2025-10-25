import os
import environ
import mimetypes
from pathlib import Path
from corsheaders.defaults import default_headers


BASE_DIR = Path(__file__).resolve().parent.parent

mimetypes.add_type("text/css", ".css", True)

env = environ.Env()
environ.Env.read_env()


SECRET_KEY = env("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '212.227.161.51',
    '212.227.161.51:8002',
    'server-timvoigt.ch',
    'www.server-timvoigt.ch',
    'timvoigt.ch',
    'quizstrike.timvoigt.ch',
]

INSTALLED_APPS = [
    # other
    'corsheaders',

    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # rest-framework
    'rest_framework',

    # apps
    'quiz',
    'category.apps.CategoryConfig',
    'question.apps.QuestionConfig',
    'answer.apps.AnswerConfig',
    'player',
    'response.apps.ResponseConfig',
    'score',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
  'http://localhost',
  'http://127.0.0.1:5500',
  'http://localhost:5500',
  'http://127.0.0.1:8000',
  'http://localhost:8000',  
  'http://localhost:4200',
  'https://server-timvoigt.ch',
  'https://timvoigt.ch',
  'https://quizstrike.timvoigt.ch',
]

CORS_ALLOWED_ORIGINS = [
  'http://localhost',
  'http://localhost:4200',
  'http://localhost:8000',  
  'https://timvoigt.ch',
  'https://server-timvoigt.ch',
]

CORS_ALLOW_CREDENTIALS = True

# CORS_ALLOW_HEADERS = list(default_headers) + [
#     'baggage',
#     'sentry-trace',
# ]

ROOT_URLCONF = 'quizstrike.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'quizstrike/templates'],
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

WSGI_APPLICATION = 'quizstrike.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/quizstrike/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'