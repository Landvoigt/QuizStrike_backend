import os
import sys
import tempfile
import environ
import mimetypes
from pathlib import Path
from corsheaders.defaults import default_headers


BASE_DIR = Path(__file__).resolve().parent.parent

mimetypes.add_type("text/css", ".css", True)

env = environ.Env()
environ.Env.read_env()


SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

if DEBUG:
    ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")
    CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    ALLOWED_HOSTS = env.list("ALLOWED_HOSTS_PROD")
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS_PROD")
    CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS_PROD")

    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    import sentry_sdk
    sentry_sdk.init(
        dsn=env("SENTRY_URL"),
        data_collection={"user_info": True},
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
        profile_session_sample_rate=env.float("SENTRY_PROFILE_SESSION_SAMPLE_RATE", default=0.1),
        profile_lifecycle="trace",
        ignore_errors=[
            "django.core.exceptions.DisallowedHost",
        ],
    )

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
REFERRER_POLICY = "no-referrer"

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    'baggage',
    'sentry-trace',
    'x-player-token',
]

ROOT_URLCONF = "quizstrike.urls"

INSTALLED_APPS = [
    # other
    "corsheaders",

    # django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # rest-framework
    "rest_framework",

    # apps
    "quiz",
    "category.apps.CategoryConfig",
    "question.apps.QuestionConfig",
    "answer.apps.AnswerConfig",
    "player",
    "response.apps.ResponseConfig",
    "score",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "quizstrike/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "quizstrike.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
        "CONN_MAX_AGE": 600,
        "CONN_HEALTH_CHECKS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/quizstrike/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

QUIZ_ANSWER_GRACE_MS = 2000

# New players per IP address; rejoining with a valid token is not counted.
# Disabled while running the test suite, which joins far more often.
TESTING = sys.argv[1:2] == ["test"]
JOIN_RATE_LIMIT = None if TESTING else env("JOIN_RATE_LIMIT", default="25/day")

REST_FRAMEWORK = {
    # Number of reverse proxies in front of the app. The client IP is read from
    # that many entries from the end of X-Forwarded-For, so it cannot be spoofed.
    "NUM_PROXIES": env.int("NUM_PROXIES", default=1),
}

# File based, so all gunicorn workers share the same rate limit counters.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": Path(tempfile.gettempdir()) / "quizstrike_cache",
        "OPTIONS": {"MAX_ENTRIES": 50000},
    }
}