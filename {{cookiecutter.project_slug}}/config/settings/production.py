# ruff: noqa: E501

from .base import *  # noqa: F403
from .base import DATABASES
from .base import INSTALLED_APPS
from .base import REDIS_URL
{%- if cookiecutter.use_drf == "y" %}
from .base import SPECTACULAR_SETTINGS
{%- endif %}
from .base import env

SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["{{ cookiecutter.domain_name }}"])

DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = "__Secure-sessionid"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = "__Secure-csrftoken"
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True,
)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF",
    default=True,
)

{% if cookiecutter.cloud_provider == 'AWS' %}
AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("DJANGO_AWS_STORAGE_BUCKET_NAME")
AWS_QUERYSTRING_AUTH = False
_AWS_EXPIRY = 60 * 60 * 24 * 7
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate",
}
AWS_S3_MAX_MEMORY_SIZE = env.int(
    "DJANGO_AWS_S3_MAX_MEMORY_SIZE",
    default=100_000_000,
)
AWS_S3_REGION_NAME = env("DJANGO_AWS_S3_REGION_NAME", default=None)
AWS_S3_CUSTOM_DOMAIN = env("DJANGO_AWS_S3_CUSTOM_DOMAIN", default=None)
aws_s3_domain = AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
{% elif cookiecutter.cloud_provider == 'GCP' %}
GS_BUCKET_NAME = env("DJANGO_GCP_STORAGE_BUCKET_NAME")
GS_DEFAULT_ACL = "publicRead"
{% elif cookiecutter.cloud_provider == 'Azure' %}
AZURE_ACCOUNT_KEY = env("DJANGO_AZURE_ACCOUNT_KEY")
AZURE_ACCOUNT_NAME = env("DJANGO_AZURE_ACCOUNT_NAME")
AZURE_CONTAINER = env("DJANGO_AZURE_CONTAINER_NAME")
{% endif -%}

{% if cookiecutter.cloud_provider != 'None' or cookiecutter.use_whitenoise == 'y' -%}
STORAGES = {
{%- if cookiecutter.use_whitenoise == 'y' and cookiecutter.cloud_provider == 'None' %}
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
{%- elif cookiecutter.cloud_provider == 'AWS' %}
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    {%- if cookiecutter.use_whitenoise == 'y' %}
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    {%- else %}
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "static",
            "default_acl": "public-read",
        },
    },
    {%- endif %}
{%- elif cookiecutter.cloud_provider == 'GCP' %}
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    {%- if cookiecutter.use_whitenoise == 'y' %}
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    {%- else %}
    "staticfiles": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "location": "static",
            "default_acl": "publicRead",
        },
    },
    {%- endif %}
{%- elif cookiecutter.cloud_provider == 'Azure' %}
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "location": "media",
            "overwrite_files": False,
        },
    },
    {%- if cookiecutter.use_whitenoise == 'y' %}
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    {%- else %}
    "staticfiles": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "location": "static",
        },
    },
    {%- endif %}
{%- endif %}
}
{%- endif %}

{%- if cookiecutter.cloud_provider == 'AWS' %}
MEDIA_URL = f"https://{aws_s3_domain}/media/"
{%- if cookiecutter.use_whitenoise == 'n' %}
COLLECTFASTA_STRATEGY = "collectfasta.strategies.boto3.Boto3Strategy"
STATIC_URL = f"https://{aws_s3_domain}/static/"
{%- endif %}
{%- elif cookiecutter.cloud_provider == 'GCP' %}
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/media/"
{%- if cookiecutter.use_whitenoise == 'n' %}
COLLECTFASTA_STRATEGY = "collectfasta.strategies.gcloud.GoogleCloudStrategy"
STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/static/"
{%- endif %}
{%- elif cookiecutter.cloud_provider == 'Azure' %}
MEDIA_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/media/"
{%- if cookiecutter.use_whitenoise == 'n' %}
COLLECTFASTA_STRATEGY = "collectfasta.strategies.azure.AzureBlobStrategy"
STATIC_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/static/"
{%- endif %}
{%- endif %}

DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="{{cookiecutter.project_name}} <noreply@{{cookiecutter.domain_name}}>",
)
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[{{cookiecutter.project_name}}] ",
)
ACCOUNT_EMAIL_SUBJECT_PREFIX = EMAIL_SUBJECT_PREFIX

ADMIN_URL = env("DJANGO_ADMIN_URL")

INSTALLED_APPS += ["anymail"]
{%- if cookiecutter.mail_service == 'Mailgun' %}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
ANYMAIL = {
    "MAILGUN_API_KEY": env("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": env("MAILGUN_DOMAIN"),
    "MAILGUN_API_URL": env("MAILGUN_API_URL", default="https://api.mailgun.net/v3"),
}
{%- elif cookiecutter.mail_service == 'Amazon SES' %}
EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
ANYMAIL = {}
{%- elif cookiecutter.mail_service == 'Mailjet' %}
EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
ANYMAIL = {
    "MAILJET_API_KEY": env("MAILJET_API_KEY"),
    "MAILJET_SECRET_KEY": env("MAILJET_SECRET_KEY"),
}
{%- elif cookiecutter.mail_service == 'Mandrill' %}
EMAIL_BACKEND = "anymail.backends.mandrill.EmailBackend"
ANYMAIL = {
    "MANDRILL_API_KEY": env("MANDRILL_API_KEY"),
    "MANDRILL_API_URL": env("MANDRILL_API_URL", default="https://mandrillapp.com/api/1.0"),
}
{%- elif cookiecutter.mail_service == 'Postmark' %}
EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"
ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": env("POSTMARK_SERVER_TOKEN"),
    "POSTMARK_API_URL": env("POSTMARK_API_URL", default="https://api.postmarkapp.com/"),
}
{%- elif cookiecutter.mail_service == 'Sendgrid' %}
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
ANYMAIL = {
    "SENDGRID_API_KEY": env("SENDGRID_API_KEY"),
    "SENDGRID_API_URL": env("SENDGRID_API_URL", default="https://api.sendgrid.com/v3/"),
}
{%- elif cookiecutter.mail_service == 'Brevo' %}
EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
ANYMAIL = {
    "BREVO_API_KEY": env("BREVO_API_KEY"),
    "BREVO_API_URL": env("BREVO_API_URL", default="https://api.brevo.com/v3/"),
}
{%- elif cookiecutter.mail_service == 'SparkPost' %}
EMAIL_BACKEND = "anymail.backends.sparkpost.EmailBackend"
ANYMAIL = {
    "SPARKPOST_API_KEY": env("SPARKPOST_API_KEY"),
    "SPARKPOST_API_URL": env("SPARKPOST_API_URL", default="https://api.sparkpost.com/api/v1"),
}
{%- elif cookiecutter.mail_service == 'Other SMTP' %}
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
ANYMAIL = {}
{%- endif %}

{% if cookiecutter.frontend_pipeline == 'Django Compressor' -%}
COMPRESS_ENABLED = env.bool("COMPRESS_ENABLED", default=True)
{%- if cookiecutter.cloud_provider == 'None' %}
COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
{%- elif cookiecutter.cloud_provider in ('AWS', 'GCP', 'Azure') and cookiecutter.use_whitenoise == 'n' %}
COMPRESS_STORAGE = STORAGES["staticfiles"]["BACKEND"]
{%- endif %}
COMPRESS_URL = STATIC_URL{% if cookiecutter.use_whitenoise == 'y' or cookiecutter.cloud_provider == 'None' %}  # noqa: F405
{%- endif -%}
{%- if cookiecutter.use_whitenoise == 'y' %}
COMPRESS_OFFLINE = True
{%- endif %}
COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.rCSSMinFilter",
    ],
    "js": ["compressor.filters.jsmin.JSMinFilter"],
}
{% endif %}
{%- if cookiecutter.use_whitenoise == 'n' and cookiecutter.cloud_provider in ('AWS', 'GCP', 'Azure') -%}
INSTALLED_APPS = ["collectfasta", *INSTALLED_APPS]
{% endif %}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

{% if cookiecutter.use_drf == "y" -%}
SPECTACULAR_SETTINGS["SERVERS"] = [
    {"url": "https://{{ cookiecutter.domain_name }}", "description": "Production server"},
]
{%- endif %}
