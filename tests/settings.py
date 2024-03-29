SECRET_KEY = "secret"


INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "tests",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
