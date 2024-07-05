"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

import dj_database_url
import sentry_sdk
from config.env import env
from django.conf.locale.en import formats as en_formats
from django.urls import reverse_lazy
from sentry_sdk.integrations.django import DjangoIntegration

is_dbt_platform = "COPILOT_ENVIRONMENT_NAME" in os.environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # django_app/
ROOT_DIR = BASE_DIR.parent  # licensing/

SECRET_KEY = env.django_secret_key

DEBUG = env.debug

ALLOWED_HOSTS = env.allowed_hosts

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

OUR_APPS = ["config", "core", "healthcheck", "feedback", "apply_for_a_licence"]

THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_forms_gds",
    "django_chunk_upload_handlers",
    "simple_history",
    "storages",
    "authbroker_client",
]

INSTALLED_APPS = DJANGO_APPS + OUR_APPS + THIRD_PARTY_APPS

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap", "bootstrap3", "bootstrap4", "uni_form", "gds")
CRISPY_TEMPLATE_PACK = "gds"

# AWS
AWS_S3_REGION_NAME = env.aws_default_region
AWS_ENDPOINT_URL = env.aws_endpoint_url

# General S3
AWS_S3_OBJECT_PARAMETERS = {"ContentDisposition": "attachment"}
PRESIGNED_URL_EXPIRY_SECONDS = env.presigned_url_expiry_seconds
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL = "private"

# Temporary document bucket
TEMPORARY_S3_BUCKET_ACCESS_KEY_ID = env.temporary_s3_bucket_configuration["access_key_id"]
TEMPORARY_S3_BUCKET_SECRET_ACCESS_KEY = env.temporary_s3_bucket_configuration["secret_access_key"]
TEMPORARY_S3_BUCKET_NAME = env.temporary_s3_bucket_configuration["bucket_name"]
AWS_ACCESS_KEY_ID = TEMPORARY_S3_BUCKET_ACCESS_KEY_ID

# Permanent document bucket
PERMANENT_S3_BUCKET_ACCESS_KEY_ID = env.permanent_s3_bucket_configuration["access_key_id"]
PERMANENT_S3_BUCKET_SECRET_ACCESS_KEY = env.permanent_s3_bucket_configuration["secret_access_key"]
PERMANENT_S3_BUCKET_NAME = env.permanent_s3_bucket_configuration["bucket_name"]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = ROOT_DIR / "static"

# Media Files Storage
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {"bucket_name": env.temporary_s3_bucket_configuration["bucket_name"], "location": "media"},
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# File storage
FILE_UPLOAD_HANDLERS = (
    "django_chunk_upload_handlers.clam_av.ClamAVFileUploadHandler",
    "core.custom_upload_handler.CustomFileUploadHandler",
)  # Order is important

# CLAM AV
CLAM_AV_USERNAME = env.clam_av_username
CLAM_AV_PASSWORD = env.clam_av_password
CLAM_AV_DOMAIN = env.clam_av_domain
CHUNK_UPLOADER_RAISE_EXCEPTION_ON_VIRUS_FOUND = False

# MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "core.middleware.CurrentSiteMiddleware",
    "django_ratelimit.middleware.RatelimitMiddleware",
]

ROOT_URLCONF = "core.urls"

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
                "django.template.context_processors.media",
                "core.sites.context_processors.sites",
                "core.context_processors.truncate_words_limit",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        **dj_database_url.parse(
            env.database_uri,
            engine="postgresql",
            conn_max_age=0,
        ),
        "ENGINE": "django.db.backends.postgresql",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# COMPANIES HOUSE API
COMPANIES_HOUSE_API_KEY = env.companies_house_api_key

# GOV NOTIFY
GOV_NOTIFY_API_KEY = env.gov_notify_api_key
EMAIL_VERIFY_CODE_TEMPLATE_ID = env.email_verify_code_template_id
RESTRICT_SENDING = env.restrict_sending  # if True, only send to whitelisted domains

# SENTRY
SENTRY_DSN = env.sentry_dsn
SENTRY_ENVIRONMENT = env.sentry_environment
if SENTRY_DSN and SENTRY_ENVIRONMENT:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0,
    )

# Email Verification settings
EMAIL_VERIFY_TIMEOUT_SECONDS = env.email_verify_timeout_seconds

# Google Analytics
GTM_ENABLED = env.gtm_enabled
GTM_ID = env.gtm_id

# Authentication - SSO
ENFORCE_STAFF_SSO = env.enforce_staff_sso

if ENFORCE_STAFF_SSO:
    AUTHENTICATION_BACKENDS = [
        "auth.view_portal_auth.ViewPortalAuth",
    ]
    AUTHBROKER_URL = env.authbroker_url
    AUTHBROKER_CLIENT_ID = env.authbroker_client_id
    AUTHBROKER_CLIENT_SECRET = env.authbroker_client_secret
    AUTHBROKER_TOKEN_SESSION_KEY = env.authbroker_token_session_key
    AUTHBROKER_STAFF_SSO_SCOPE = env.authbroker_staff_sso_scope

    OAUTHLIB_INSECURE_TRANSPORT = env.oauthlib_insecure_transport

    LOGIN_URL = reverse_lazy("authbroker_client:login")
    # TODO: update when viewing portal is created
    LOGIN_REDIRECT_URL = reverse_lazy("view_a_suspected_breach:landing")
else:
    LOGIN_URL = "/admin/login"

TRUNCATE_WORDS_LIMIT = 30

en_formats.DATE_FORMAT = "d/m/Y"

# Django sites
APPLY_FOR_A_LICENCE_DOMAIN = env.apply_for_a_licence_domain
VIEW_A_LICENCE_DOMAIN = env.view_a_licence_domain

# Django Ratelimit
RATELIMIT_VIEW = "core.views.base_views.rate_limited_view"
RATELIMIT = "10/m"
