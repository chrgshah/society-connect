# Override base settings for development
DEBUG = True
ALLOWED_HOSTS = ["*"]
CSRF_COOKIE_SECURE = False
JWT_COOKIE_SECURE = False

DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'society_connect',
            'USER': 'mysuperuser',
            'PASSWORD': 'mysuperuser',
            'HOST': 'localhost',
            'PORT': '5432',
        }
}
