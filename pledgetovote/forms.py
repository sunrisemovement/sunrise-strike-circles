from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from pledgetovote.models import StrikeCircle


class SignupForm(forms.ModelForm):
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)
    name = forms.CharField(label="Strike Circle name", max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput,
            'password2': forms.PasswordInput
        }
        labels = {
            'username': "Strike Circle username"
        }

    def clean_password2(self):
        pass1 = self.cleaned_data['password']
        pass2 = self.cleaned_data['password2']

        if pass1 and pass2 and pass1 != pass2:
            raise ValidationError("Passwords do not match")

        return pass2

    def save(self, **kwargs):
        data = self.cleaned_data
        user = User(
            username = data['username'],
            email = data['email'],
        )
        user.set_password(data['password'])
        user.save()
        return user


class StrikeCircleCreateForm(forms.ModelForm):

    class Meta:
        model = StrikeCircle
        fields = ['name']
        labels = {
            'name': "Strike Circle name"
        }
