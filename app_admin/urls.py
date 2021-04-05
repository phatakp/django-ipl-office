from django.urls import path
from . import views

app_name = 'app_admin'

urlpatterns = [
    path('<str:typ>/', views.MainView.as_view(), name='main'),
]
