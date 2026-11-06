from pathlib import Path
from .conf import SECRET_KEY, DEBUG
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = SECRET_KEY
DEBUG = DEBUG

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'apps.auths',
    'apps.blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'hw1' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'
ASGI_APPLICATION = 'settings.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'


AUTH_USER_MODEL = 'auths.User'

UNFOLD = {
    "SITE_TITLE": "Мой Блог",
    "SITE_HEADER": "Управление блогом",
    "SITE_ICON": "rocket", 
    "DASHBOARD_CALLBACK": "apps.blog.callbacks.dashboard_callback",

    "COLORS": {
        "primary": { 
            "50": "250 253 255",
            "100": "241 249 255",
            "200": "225 242 254",
            "300": "186 228 253",
            "400": "141 207 252",
            "500": "84 174 250",
            "600": "43 134 245",
            "700": "26 103 227",
            "800": "27 82 191",
            "900": "28 70 151",
            "950": "21 44 91",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "ОБЗОР",
                "separator": True,
                "items": [
                    {"title": "Дашборд", "icon": "dashboard", "link": reverse_lazy("admin:index")},
                ],
            },
            {
                "title": "КОНТЕНТ",
                "separator": True,
                "items": [
                    {"title": "Посты", "icon": "article", "link": reverse_lazy("admin:blog_post_changelist")},
                    {"title": "Комментарии", "icon": "forum", "link": reverse_lazy("admin:blog_comment_changelist")},
                    {"title": "Категории", "icon": "category", "link": reverse_lazy("admin:blog_category_changelist")},
                    {"title": "Теги", "icon": "label", "link": reverse_lazy("admin:blog_tag_changelist")},
                ],
            },
            {
                "title": "ПОЛЬЗОВАТЕЛИ И ДОСТУП",
                "separator": True,
                "items": [
                    {"title": "Группы", "icon": "shield", "link": reverse_lazy("admin:auth_group_changelist")},
                ],
            },
        ],
    },
}