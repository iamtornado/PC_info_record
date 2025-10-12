from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('computers/', views.computer_list_api, name='computer_list_api'),  # GET for list
    path('computers/create/', views.create_computer, name='create_computer'),  # POST for create
    path('computers/<int:pk>/', views.computer_detail_api, name='computer_detail_api'),
]
