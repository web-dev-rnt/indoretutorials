"""
Django settings for eduTrellis project (Django 5.2+ ready).
Optimized for performance, caching, security, and Core Web Vitals.
"""

from pathlib import Path
import os
import dj_database_url

# --------------------
# BASE SETTINGS
# --------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "local-development-key-4fY9uL2qN7vR8xW3sA6dH1jK5mP0tC9bE2gZ7nQ4",
)

DEBUG = True

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,testserver,www.thevedaeducation.info,"
        "ganeshsirclasses.online,www.ganeshsirclasses.online,"
        "indoretutorials.online,www.indoretutorials.online,"
        "web-production-ab46.up.railway.app",
    ).split(",")
    if host.strip()
]

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
    "adminpanel.middleware.ManagementAccessMiddleware",
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
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
    DATABASES["default"].setdefault("OPTIONS", {})["timeout"] = 20

# --------------------
# CACHING
# LocMemCache is zero-dependency and ideal for single-process deployments (Railway)
# --------------------
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "TIMEOUT": 300,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "edutrellis-cache",
            "TIMEOUT": 300,
            "OPTIONS": {"MAX_ENTRIES": 1000},
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
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
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

X_FRAME_OPTIONS = "DENY"

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# --------------------
# LOGIN / LOGOUT
# --------------------
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"
LOGIN_URL = "/login/"

# --------------------
# THIRD-PARTY INTEGRATIONS
# --------------------
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")

JITSI_DOMAIN = os.environ.get("JITSI_DOMAIN", "meet.jit.si")

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
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "https://www.thevedaeducation.info,"
        "https://ganeshsirclasses.online,https://www.ganeshsirclasses.online,"
        "https://indoretutorials.online,https://www.indoretutorials.online,"
        "https://web-production-ab46.up.railway.app",
    ).split(",")
    if origin.strip()
]

# --------------------
# DROPBOX STORAGE
# --------------------
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY", "")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET", "")
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN", "")

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
