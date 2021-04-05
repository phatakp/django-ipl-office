from django.contrib.auth import get_user_model
from django import forms

CustomUser = get_user_model()


class TeamChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('team',)
