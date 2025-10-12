"""
URL configuration for pc_info_record project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from computers import views as computer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', computer_views.login_view, name='login'),
    path('logout/', computer_views.logout_view, name='logout'),
    path('', include('computers.urls')),
    path('api/', include('api.urls')),
]

# 开发环境下提供静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
