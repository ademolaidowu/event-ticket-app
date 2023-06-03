"""
    Django settings for local or development stages.
"""


from .base import *


# ==============================================================================
# DATABASES SETTINGS
# ==============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR.parent / "db.sqlite3",
    }
}




# ==============================================================================
# EMAIL SETTINGS
# ==============================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default=" ")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default=" ")




# ==============================================================================
# THIRD PARTY PACKAGES
# ==============================================================================

# SWAGGER SETTINGS #

SWAGGER_SETTINGS={
    'SECURITY_DEFINITIONS':{
        'Bearer':{
            'type':'apiKey',
            'name':'Authorization',
            'in':'header'
        }
    }
}

