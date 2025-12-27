from .base import *  # noqa: F403
from .base import INSTALLED_APPS
from .base import MIDDLEWARE
from .base import env

DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="!!!SET DJANGO_SECRET_KEY!!!!",
)
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

{%- if cookiecutter.use_mailpit == 'y' and cookiecutter.use_docker == 'y' -%}
EMAIL_HOST = env("EMAIL_HOST", default="mailpit")
EMAIL_PORT = 1025
{%- elif cookiecutter.use_mailpit == 'y' and cookiecutter.use_docker == 'n' -%}
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
{%- else -%}
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend",
)
{%- endif %}

{%- if cookiecutter.use_whitenoise == 'y' %}
INSTALLED_APPS = ["whitenoise.runserver_nostatic", *INSTALLED_APPS]
{% endif %}

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
{% if cookiecutter.use_docker == 'y' -%}
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join([*ip.split(".")[:-1], "1"]) for ip in ips]
    {%- if cookiecutter.windows == 'y' %}
    RUNSERVERPLUS_POLLER_RELOADER_TYPE = 'stat'
    RUNSERVERPLUS_POLLER_RELOADER_INTERVAL = 1
    {%- endif %}
{%- endif %}

INSTALLED_APPS += ["django_extensions"]
{% if cookiecutter.use_celery == 'y' -%}
{%- if cookiecutter.use_docker == 'n' -%}
CELERY_TASK_ALWAYS_EAGER = True
{%- endif %}
CELERY_TASK_EAGER_PROPAGATES = True
{%- endif %}
