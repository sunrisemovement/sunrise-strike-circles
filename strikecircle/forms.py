from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from strikecircle.models import Pledge, StrikeCircle


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


class StrikeCircleEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        # Don't allow Strike Circle goals to be changed once they've been set to something other than 0
        if instance:
            if instance.pledge_goal > 0:
                self.fields['pledge_goal'].disabled = True
            if instance.one_on_one_goal > 0:
                self.fields['one_on_one_goal'].disabled = True

    class Meta:
        model = StrikeCircle
        fields = ['name', 'pledge_goal', 'one_on_one_goal']
        labels = {
            'name': "Strike Circle name",
            'pledge_goal': "Pledge goal (can't be edited once set)",
            'one_on_one_goal': "One-on-one goal (can't be edited once set)"
        }

class PledgeForm(forms.ModelForm):
    class Meta:
        model = Pledge
        fields = ['first_name', 'last_name', 'email', 'phone', 'zipcode', 'yob', 'date_collected', 'one_on_one']

class CreatePledgeForm(forms.ModelForm):
    Meta = PledgeForm.Meta

    def has_changed(self):
        changed = super().has_changed()
        # Don't report the form as changed if only the date_collected field is changed, because that field is
        # autofilled from a cookie every time a new form row is rendered
        if self.changed_data == ['date_collected']:
            changed = False
        return changed

PledgeFormSet = forms.modelformset_factory(Pledge, extra=0, form=PledgeForm, can_delete=True)
CreatePledgeFormSet = forms.modelformset_factory(Pledge, extra=0, form=CreatePledgeForm, can_delete=True)
