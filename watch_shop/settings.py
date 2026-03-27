import os
from pathlib import Path

# 1. Đường dẫn gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Bảo mật (Giữ nguyên hoặc thay đổi tùy ý)
SECRET_KEY = 'django-insecure-chuyen-dong-ho-xin'
DEBUG = True
ALLOWED_HOSTS = []

# 3. Các ứng dụng đã cài đặt
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # BẮT BUỘC có dòng này để dùng được |intcomma trong HTML
    'django.contrib.humanize', 
    
    # App của bạn
    'products',
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

ROOT_URLCONF = 'watch_shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Đảm bảo Django tìm đúng thư mục templates
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.cart_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'watch_shop.wsgi.application'

# 4. Cơ sở dữ liệu
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 5. CẤU HÌNH QUAN TRỌNG ĐỂ HIỆN DẤU CHẤM TIỀN
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True

# PHẢI ĐỂ FALSE để Django dùng THOUSAND_SEPARATOR của mình
USE_L10N = False 

USE_TZ = True

# Định dạng số kiểu Việt Nam: 180.000.000
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
NUMBER_GROUPING = 3

# 6. File tĩnh (CSS, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 7. Cấu hình Đăng nhập/Đăng xuất
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'