from django import forms

from pledgetovote.models import Address, Location, Passcode, Pledge


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'


class AuthForm(forms.Form):
    passcode = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput
    )


class LocationForm(forms.Form):

    select_location = forms.CharField(required=False)
    create_new_location = forms.BooleanField(required=False)
    new_location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': "Create a new location..."})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        locations = Location.objects.all()
        self.location_choices = [(loc.id, loc.name) for loc in locations]
        self.locs_exist = len(locations) > 0

        # Disable select_location field if no Locations exist
        self.fields['select_location'].widget = forms.Select(
            attrs={'disabled': not self.locs_exist},
            choices=self.location_choices or [('UNSELECTABLE', "No locations exist")]
        )

        self.fields['create_new_location'].initial = not self.locs_exist
        # Disable the create_new_location field if no Locations exist, to force the user to create a Location
        self.fields['create_new_location'].widget = forms.CheckboxInput(attrs={'disabled': not self.locs_exist})

        # If any locations exist, disable the new_location by default
        self.fields['new_location'].widget.disabled = self.locs_exist