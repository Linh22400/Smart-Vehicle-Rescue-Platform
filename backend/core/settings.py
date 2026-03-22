import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file (silently ignored if not present)
load_dotenv(BASE_DIR / '.env')

# ─── Security ────────────────────────────────────────────────────────────────
_secret = os.environ.get('DJANGO_SECRET_KEY', '')
if not _secret:
    import warnings
    _secret = 'django-insecure-dev-only-key-change-before-production'
    warnings.warn(
        "\n\n⚠️  DJANGO_SECRET_KEY is not set in .env! "
        "Using insecure dev key. DO NOT use in production!\n",
        RuntimeWarning, stacklevel=2
    )
SECRET_KEY = _secret
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


# Application definition
INSTALLED_APPS = [
    'jazzmin',                      # Phải đặt trước django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.users',
    'apps.bookings',
    'apps.ai_engine',
    'apps.services',
]

# ─── Cấu hình giao diện Jazzmin Admin ───────────────────────────────────────
JAZZMIN_SETTINGS = {
    # Tiêu đề và logo
    'site_title': 'SmartRescue Admin',
    'site_header': '🚗 Smart Vehicle Rescue Platform',
    'site_brand': 'SmartRescue',
    'welcome_sign': 'Chào mừng đến Trang Quản Trị Hệ Thống',
    'copyright': 'Smart Vehicle Rescue Platform © 2026',

    # Icon cho từng model trong sidebar
    'icons': {
        'auth':                     'fas fa-users-cog',
        'auth.user':                'fas fa-user',
        # Khai báo icon cho nhóm App gốc (Tên App hiển thị in đậm)
        'users':                    'fas fa-id-card',
        'bookings':                 'fas fa-map-marked-alt',
        'services':                 'fas fa-briefcase',
        'ai_engine':                'fas fa-brain',
        
        # Khai báo icon riêng cho Model
        'users.customuser':         'fas fa-user-circle',
        'users.mechanicprofile':    'fas fa-wrench',
        'users.mechanicperformance':'fas fa-chart-bar',
        'bookings.booking':         'fas fa-ambulance',
        'bookings.chatmessage':     'fas fa-comments',
        'bookings.complaint':       'fas fa-user-shield',
        'services.service':         'fas fa-tools',
        'services.appointment':     'fas fa-calendar-check',
        'services.review':          'fas fa-star',
        'ai_engine.aireport':       'fas fa-robot',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-dot-circle',

    # Giao diện & hành vi
    'show_sidebar': True,
    'navigation_expanded': True,
    'hide_apps': [],
    'hide_models': [],
    'order_with_respect_to': [
        'users', 'bookings', 'services', 'ai_engine',
    ],

    # Liên kết nhanh trên header
    'topmenu_links': [
        {'name': 'Trang chủ', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': '🌐 Xem App', 'url': 'http://localhost:5173', 'new_window': True},
    ],

    # Hiển thị avatar và thông tin user trên sidebar
    'usermenu_links': [
        {'name': 'Hỗ trợ', 'url': 'https://github.com', 'new_window': True, 'icon': 'fas fa-life-ring'},
    ],

    # Tìm kiếm model nhanh
    'search_model': ['users.customuser', 'bookings.booking'],
    'show_ui_builder': False,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-danger',       # Màu đỏ chủ đạo
    'accent': 'accent-danger',
    'navbar': 'navbar-dark',
    'no_navbar_border': True,
    'navbar_fixed': True,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-danger',      # Sidebar tối màu đỏ
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'darkly',                     # Theme tối
    'dark_mode_theme': 'darkly',
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-outline-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success'
    },
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Added - Must be top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
AUTH_USER_MODEL = 'users.CustomUser'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AI Configuration - Google Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# CORS CONFIGURATION
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# CSRF CONFIGURATION
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# REST FRAMEWORK CONFIG
# Using a custom authentication class to bypass CSRF for MVP demo purposes
# (Since frontend is separate and we want to reuse Admin Session easily)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.core.authentication.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
