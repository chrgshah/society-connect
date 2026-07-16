# Override base settings for development
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'society-connect',
            'USER': 'mysuperuser',
            'PASSWORD': 'mysuperuser',
            'HOST': 'localhost',
            'PORT': '5432',
        }
}
