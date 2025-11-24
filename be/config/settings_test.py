"""
Test-specific Django settings.
Inherits from base settings but overrides for CI/CD environments.
"""
from .settings import *
import os

# Override database for tests if DATABASE_URL is provided
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(
        default=os.environ['DATABASE_URL'],
        conn_max_age=600
    )

# Disable MinIO for tests
os.environ['MINIO_ENABLED'] = 'false'

# Use in-memory file storage for tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Simplified password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations during tests (optional, speeds up tests)
# Uncomment if you want faster tests but be aware of potential issues
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

# Disable debug toolbar and other debug tools
DEBUG = False

# Allow all hosts in test
ALLOWED_HOSTS = ['*']

# Simplified logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
