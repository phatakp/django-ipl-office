from django.urls import path

from . import views

app_name = 'app_matches'

urlpatterns = [
    path('schedule/<str:typ>/', views.ScheduleView.as_view(), name='schedule'),
    path('detail/<int:pk>/',
         views.MatchDetailView.as_view(), name='detail'),
]
