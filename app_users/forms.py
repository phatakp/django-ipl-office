from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django import forms

CustomUser = get_user_model()


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'name',
                  'password1', 'password2', 'team')
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'Enter Your Name'}),
                   'email': forms.EmailInput(attrs={'placeholder': 'Enter Your Email'}),
                   'password1': forms.PasswordInput(attrs={'placeholder': 'Password'}),
                   'password2': forms.PasswordInput(attrs={'placeholder': 'Retype Password'}),
                   }
        labels = {'name': 'Name',
                  'email': 'Email',
                  'password1': 'Password',
                  'password2': 'Confirm Password',
                  'team': "IPL Winner (300 points to be staked)"}

    def clean_name(self):
        name = self.cleaned_data.get('name', None)
        if name is None:
            raise forms.ValidationError('Name is Mandatory')
        else:
            return name

    def clean_team(self):
        team = self.cleaned_data.get('team', None)
        if team is None:
            raise forms.ValidationError('Team Selection is Mandatory')
        else:
            return team


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password')
        widgets = {'username': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
                   'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
                   }


class UserPwdChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ('old_password',
                  'new_password1',
                  'new_password2',
                  )


class UserPwdResetForm(forms.Form):
    email = forms.EmailField(label='Email Address',
                             required=True, widget=forms.EmailInput())
    new_password1 = forms.CharField(
        label="New Password", required=True, widget=forms.PasswordInput())
    new_password2 = forms.CharField(
        label="Confirm Password", required=True, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required')
        else:
            try:
                user = CustomUser.objects.get(email=email)
            except:
                raise ValidationError('No user exists with this email')
            else:
                new_password1 = cleaned_data.get('new_password1')
                new_password2 = cleaned_data.get('new_password2')
                if new_password1 and new_password2:
                    if new_password1 != new_password2:
                        raise ValidationError('Both Passwords dont match')
                else:
                    raise ValidationError('Password fields are mandatory')
