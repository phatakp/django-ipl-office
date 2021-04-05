from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'app_users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='login.html'), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('pwdchg/', views.UserPwdChangeView.as_view(), name='pwd_change'),
    path('pwdreset/', views.UserPwdResetView.as_view(), name='pwd_reset'),
]
