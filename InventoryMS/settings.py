import os
import dj_database_url
from pathlib import Path
from decouple import config

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent


# Security
SECRET_KEY = config('SECRET_KEY', default='django-insecure-g_n2+2bznu6e@1wel!i(&-4tp86_7lop5395ww+i4x%9*7^old')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['.vercel.app', 'localhost', '127.0.0.1', '*']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']


# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'django_extensions',
    'tinymce',
    'django_countries',

    # Project apps
    'accounts',
    'catalogue',
    'shop',
    'cart',
    'orders',
    'stockpile',
    'pos',
    'invoice',
    'bills',
    'audit',
    'reviews',
    'reports',
]


# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit.middleware.auditMiddleware',
]


# URL / WSGI
ROOT_URLCONF = 'InventoryMS.urls'
WSGI_APPLICATION = 'InventoryMS.wsgi.application'


# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_context',
                'orders.context_processors.orders_context',
                'shop.context_processors.categories_context',
            ],
        },
    },
]


# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=True if not config('DEBUG', default=True, cast=bool) else False,
    )
}


# Auth
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',           # primary: login by email
    'django.contrib.auth.backends.ModelBackend', # fallback: admin/manage.py
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:customer_dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalisation
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True


# Static & Media
# Static & Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Cloud Storage (Supabase S3) for Media
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1') # Supabase default

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_QUERYSTRING_AUTH = False  # Disable signed URLs for public assets
AWS_S3_SIGNATURE_VERSION = 's3v4' 

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
    'ACL': 'public-read',
}

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Generate the public Supabase URL format for link generation
SUPABASE_PROJECT_ID = AWS_S3_ENDPOINT_URL.split('//')[1].split('.')[0] if AWS_S3_ENDPOINT_URL else ''
AWS_S3_CUSTOM_DOMAIN = f"{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/{AWS_STORAGE_BUCKET_NAME}"

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
MEDIA_ROOT = BASE_DIR / 'media'


# Default PK
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email — Gmail API
# Email — Gmail API

EMAIL_BACKEND = 'utils.gmail_backend.GmailAPIBackend'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='AURA Jewellery <noreply@aurajewellery.com>')

GMAIL_CLIENT_ID = config('GMAIL_CLIENT_ID', default='')
GMAIL_CLIENT_SECRET = config('GMAIL_CLIENT_SECRET', default='')
GMAIL_CLIENT_SECRET_PATH = config('GMAIL_CLIENT_SECRET_PATH', default='')

# Dynamic Site URL for Vercel
VERCEL_ENV_URL = config('VERCEL_URL', default=None)
if VERCEL_ENV_URL:
    SITE_URL = f"https://{VERCEL_ENV_URL}"
else:
    SITE_URL = config('SITE_URL', default='http://127.0.0.1:8000')

CSRF_TRUSTED_ORIGINS = [f"https://{VERCEL_ENV_URL}"] if VERCEL_ENV_URL else ['https://*.vercel.app']


# Stockpile Fee
STOCKPILE_FREE_DAYS = 30
STOCKPILE_DAILY_FEE = 200   # NGN

TINYMCE_DEFAULT_CONFIG = {
    'license_key': 'gpl',
    'height': 500,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'menubar': True,
    'statusbar': True,
    'plugins': '''
        save link image media preview codesample
        table code lists fullscreen insertdatetime nonbreaking
        directionality searchreplace wordcount visualblocks
        visualchars autolink charmap anchor pagebreak
    ''',
    'toolbar': '''
        undo redo | blocks | bold italic underline strikethrough | 
        forecolor backcolor | alignleft aligncenter alignright alignjustify | 
        bullist numlist outdent indent | link image media table | 
        codesample | code fullscreen preview | removeformat
    ''',
    'contextmenu': 'link image table',
    
    'block_formats': 'Paragraph=p; Heading 2=h2; Heading 3=h3; Heading 4=h4; Heading 5=h5; Heading 6=h6; Preformatted=pre',
    
    'content_style': '''
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: #1f2937;
            background-color: #ffffff;
            max-width: 100%;
            padding: 16px;
        }
        h2 { font-size: 1.5rem; font-weight: 700; margin-top: 1.25rem; margin-bottom: 0.5rem; color: #111827; }
        h3 { font-size: 1.25rem; font-weight: 700; margin-top: 1rem; margin-bottom: 0.4rem; color: #1f2937; }
        h4 { font-size: 1.125rem; font-weight: 600; margin-top: 0.875rem; margin-bottom: 0.35rem; color: #1f2937; }
        h5 { font-size: 1rem; font-weight: 600; margin-top: 0.75rem; margin-bottom: 0.3rem; color: #374151; }
        h6 { font-size: 0.875rem; font-weight: 600; margin-top: 0.625rem; margin-bottom: 0.25rem; color: #4b5563; }
        p { margin-bottom: 0.75rem; color: #00000; }
        ul, ol { margin-bottom: 0.75rem; padding-left: 1.5rem; color: #374151; }
        li { margin-bottom: 0.25rem; }
        img { max-width: 100%; height: auto; border-radius: 0.375rem; margin: 0.75rem 0; }
        blockquote { border-left: 3px solid #10b981; padding: 0.5rem 0.75rem; margin: 0.75rem 0; font-style: italic; color: #6b7280; background-color: #f9fafb; border-radius: 0 0.25rem 0.25rem 0; }
        code { background-color: #f3f4f6; padding: 0.15rem 0.35rem; border-radius: 0.25rem; color: #dc2626; font-size: 0.9em; }
        pre { background-color: #1f2937; padding: 0.75rem; border-radius: 0.375rem; overflow-x: auto; color: #e5e7eb; }
        a { color: #2563eb; }
        table { border-collapse: collapse; width: 100%; margin: 0.75rem 0; }
        th, td { border: 1px solid #e5e7eb; padding: 0.5rem; color: #374151; }
        th { background-color: #f9fafb; font-weight: 600; }
    ''',
    
    'valid_elements': '*[*]',
    'extended_valid_elements': 'img[class|src|border=0|alt|title|hspace|vspace|width|height|align|name]',
    'newline_behavior': 'block',
    'remove_trailing_brs': True,
    
    'browser_spellcheck': True,
    'relative_urls': False,
    'remove_script_host': False,
    'convert_urls': True,
    
    
    'images_upload_url': '/tinymce/upload/',
    'automatic_uploads': True,
    'images_reuse_filename': True,
    'file_picker_types': 'image',
    'images_file_types': 'jpg,jpeg,png,gif,webp',
}