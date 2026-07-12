"""
Django settings for eduTrellis project (Django 5.2+ ready).
Optimized for performance, caching, security, and Core Web Vitals.
"""

from pathlib import Path
import os

# --------------------
# BASE SETTINGS
# --------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = "django-insecure-h^l!e0kvn8ore3fikloht@x^6nlif_jbgg$=x=!0b(v-lu#ev_"

DEBUG = True

ALLOWED_HOSTS = ['*']

# --------------------
# APPLICATIONS
# --------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "base",
    "live_class",
    "elibrary",
    "testseries",
    "video_courses",
    "adminpanel",
]

# --------------------
# MIDDLEWARE
# (GZipMiddleware first for maximum compression coverage)
# --------------------
MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "eduTrellis.urls"

# --------------------
# TEMPLATES
# Cached template loader reduces template parsing overhead significantly
# --------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,  # Must be False when using loaders explicitly
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Custom context processors
                "adminpanel.context_processors.navbar_settings",
                "adminpanel.context_processors.footer_settings",
                "adminpanel.context_processors.site_contact",
                "video_courses.context_processors.categories_context",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
        },
    },
]

WSGI_APPLICATION = "eduTrellis.wsgi.application"

# --------------------
# DATABASE
# CONN_MAX_AGE=600 enables persistent DB connections (no reconnect overhead per request)
# --------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'timeout': 20,
        },
    }
}

# --------------------
# CACHING
# LocMemCache is zero-dependency and ideal for single-process deployments (Railway)
# --------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "edutrellis-cache",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }
}

# --------------------
# SESSIONS
# cached_db backend: reads from fast cache, writes to DB for persistence
# --------------------
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

# --------------------
# PASSWORD VALIDATION
# --------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------
# INTERNATIONALIZATION
# --------------------
LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --------------------
# STATIC & MEDIA FILES
# --------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# WhiteNoise: serve compressed static files with aggressive browser caching (1 year)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_ALLOW_ALL_ORIGINS = True

# --------------------
# CUSTOM USER MODEL
# --------------------
AUTH_USER_MODEL = "base.User"

# --------------------
# SECURITY HEADERS
# --------------------
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

X_FRAME_OPTIONS = "SAMEORIGIN"

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# --------------------
# LOGIN / LOGOUT
# --------------------
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# --------------------
# THIRD-PARTY INTEGRATIONS
# --------------------
RAZORPAY_KEY_ID = 'rzp_test_RaygzMDa8nwFFP'
RAZORPAY_KEY_SECRET = 'F1mtVXEvOvbyc6atPUAEwdZd'

JITSI_DOMAIN = "meet.ffmuc.net"

# --------------------
# DEFAULTS
# --------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CSRF cookie readable by JS (needed for AJAX payment flow)
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

# --------------------
# PWA SETTINGS
# --------------------
PWA_APP_NAME = 'EduTrellis'
PWA_APP_DESCRIPTION = 'Premium online education platform'
PWA_APP_THEME_COLOR = '#c7212f'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'portrait-primary'
PWA_APP_START_URL = '/'

PWA_APP_ICONS = [
    {'src': '/static/img/icon-192.png', 'sizes': '192x192'},
    {'src': '/static/img/icon-512.png', 'sizes': '512x512'},
]

# --------------------
# CSRF TRUSTED ORIGINS
# --------------------
CSRF_TRUSTED_ORIGINS = [
    "https://www.thevedaeducation.info",
    "https://ganeshsirclasses.online",
    "https://www.ganeshsirclasses.online",
    "https://web-production-ab46.up.railway.app",
]

# --------------------
# DROPBOX STORAGE
# --------------------
DEFAULT_FILE_STORAGE = "edutrellis.dropbox_storage.DropboxStorage"

DROPBOX_APP_KEY = "wgg2fsw5pf16x8q"
DROPBOX_APP_SECRET = "38dg9gi6djz3zuu"
DROPBOX_REFRESH_TOKEN = "Si57f7yXuB0AAAAAAAAAAZGrsYbd1YLQpvGHxlJES4DRvKr7mDfZo8xqLaJBTY_s"

# --------------------
# LOGGING
# --------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "base": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
