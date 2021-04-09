from django.apps import apps
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.utils import timezone
from django.db.models import F

from .forms import UserRegistrationForm, UserLoginForm, UserPwdChangeForm, UserPwdResetForm

CustomUser = get_user_model()
Bet = apps.get_model('app_matches', 'Bet')
Match = apps.get_model('app_matches', 'Match')


class UserLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        return super().form_valid(form)


class UserRegistrationView(FormView):
    template_name = 'register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('app_users:login')

    def form_valid(self, form):
        # Register User
        user = form.save()

        # Save IPL Winner bet for Rs. 250
        Bet.objects.create(user=user,
                           bet_team=user.team,
                           bet_amt=300,
                           status='P')
        completed = Match.objects.filter(
            datetime__lt=timezone.localtime()).count()
        if completed > 0:
            user.curr_amt = F('curr_amt') - (completed * 20)
            user.save()
        return super().form_valid(form)


class UserPwdChangeView(PasswordChangeView):
    template_name = 'pwd_change.html'
    form_class = UserPwdChangeForm
    success_url = reverse_lazy('app_users:pwd_change')

    def get_form_kwargs(self):
        kwargs = super(UserPwdChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        context = self.get_context_data()
        context['message'] = "Your Password has been changed successfully!"
        return render(self.request, self.template_name, context)


class UserPwdResetView(FormView):
    template_name = 'pwd_reset.html'
    form_class = UserPwdResetForm
    success_url = reverse_lazy('app_users:pwd_reset')

    def form_valid(self, form):
        # Get user object
        user = CustomUser.objects.get(
            email=form.cleaned_data.get('email'))

        # Set new password and save
        user.set_password(form.cleaned_data.get('new_password1'))
        user.save()

        context = self.get_context_data()
        context['message'] = "Your Password has been changed successfully!"
        return render(self.request, self.template_name, context)
