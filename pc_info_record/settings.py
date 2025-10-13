"""
Django settings for pc_info_record project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# CSRF 信任的源（Django 4.0+ 必需）
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost,https://localhost,http://127.0.0.1,https://127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'computers',
    'api',
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

ROOT_URLCONF = 'pc_info_record.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'pc_info_record.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'pc_info_record'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Password validation
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
]

# Internationalization
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'zh-hans')
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Shanghai')
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 开发环境中的静态文件目录（如果存在）
if os.path.exists(BASE_DIR / 'static'):
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
else:
    STATICFILES_DIRS = []

# Media files (User uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'] if os.getenv('DOCKER_CONTAINER') else ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django_auth_ldap': {
            'handlers': ['console'] if os.getenv('DOCKER_CONTAINER') else ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# ==============================================================================
# LDAP/Active Directory 认证配置
# ==============================================================================

import ldap
from django_auth_ldap.config import LDAPSearch

# 启用LDAP认证后端
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',  # LDAP/AD认证
    'django.contrib.auth.backends.ModelBackend',  # Django默认认证（用于超级用户）
]

# LDAP服务器配置
AUTH_LDAP_SERVER_URI = os.getenv('LDAP_SERVER_URI', 'ldap://192.168.124.7:389')

# 绑定DN和密码（用于查询AD的服务账号）
AUTH_LDAP_BIND_DN = os.getenv('LDAP_BIND_DN', 'CN=it.django,OU=SpecialAccount,OU=myse,DC=dltornado2,DC=com')
AUTH_LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PASSWORD', '')

# 用户搜索配置
# 在 OU=myse,DC=dltornado2,DC=com 下搜索用户
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.getenv('LDAP_USER_BASE_DN', 'OU=myse,DC=dltornado2,DC=com'),
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)"  # 使用Windows登录名搜索
)

# 用户属性映射：将AD属性映射到Django用户模型
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",  # 名
    "last_name": "sn",          # 姓
    "email": "mail",            # 邮箱
}

# 用户标志设置
# 注意: AUTH_LDAP_USER_FLAGS_BY_GROUP 用于根据AD组成员身份设置权限
# 如果需要根据AD组设置权限，可以这样配置:
# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#     "is_active": "CN=active_users,OU=Groups,OU=myse,DC=dltornado2,DC=com",
#     "is_staff": "CN=IT_Staff,OU=Groups,OU=myse,DC=dltornado2,DC=com",
#     "is_superuser": "CN=Admins,OU=Groups,OU=myse,DC=dltornado2,DC=com",
# }

# 暂不使用组权限，所有LDAP用户默认可以登录
# Django默认行为: is_active=True, is_staff=False, is_superuser=False

# 首次登录时自动创建用户
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# 允许创建新用户
AUTH_LDAP_NO_NEW_USERS = False

# 缓存LDAP查询结果（3600秒 = 1小时）
AUTH_LDAP_CACHE_TIMEOUT = 3600

# LDAP连接选项
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 0,
    ldap.OPT_REFERRALS: 0,  # 不跟随引用
}

# 登录和登出URL配置
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# 会话安全配置
SESSION_COOKIE_AGE = 3600  # 会话1小时后过期
SESSION_SAVE_EVERY_REQUEST = True  # 每次请求都更新会话

# ==============================================================================
# 生产环境安全配置
# ==============================================================================

# 仅在生产环境启用的安全设置
if not DEBUG:
    # HTTPS 相关
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # 其他安全设置
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
    # 代理相关（Nginx 反向代理）
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

# CORS 设置（如果需要跨域访问）
# CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# CSRF 信任的源
CSRF_TRUSTED_ORIGINS = [
    origin.strip() 
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1').split(',')
    if origin.strip()
]
