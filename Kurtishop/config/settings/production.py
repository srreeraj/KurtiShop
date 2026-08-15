from .base import *


# ============================================================
# PRODUCTION
# ============================================================

DEBUG = False


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = env("SECRET_KEY")


# ============================================================
# HOSTS
# ============================================================

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS"
)


# ============================================================
# HTTPS / SECURITY
# ============================================================

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)

CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)

SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True


# ============================================================
# BROWSER SECURITY
# ============================================================

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = "same-origin"

X_FRAME_OPTIONS = "DENY"