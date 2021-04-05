from django.urls import path
from . import views

app_name = 'app_main'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('team/<str:name>/', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('team_change/', views.TeamChangeView.as_view(), name='team_change'),
    path('game_rules/', views.RulesView.as_view(), name='rules'),
]
