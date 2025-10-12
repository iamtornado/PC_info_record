from django.urls import path
from . import views

app_name = 'computers'

urlpatterns = [
    path('', views.computer_list, name='computer_list'),
    path('search/', views.search, name='search'),
    path('<int:pk>/', views.computer_detail, name='computer_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
