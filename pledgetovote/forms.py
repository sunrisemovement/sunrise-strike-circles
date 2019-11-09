from django import forms

from pledgetovote.models import Address, Location, Pledge

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'


class LocationForm(forms.Form):
    locations = Location.objects.all()
    location_choices = [(loc.id, loc.name) for loc in locations]
    locs_exist = len(locations)

    select_location = forms.CharField(
        required=False,
        # Disable this field if no Locations exist
        widget=forms.Select(
            attrs={'disabled': not locs_exist},
            choices=location_choices
        )
    )
    create_new_location = forms.BooleanField(
        initial=(not locs_exist),
        required=False,
        # Disable this field if no Locations exist, to force the user to create a Location
        widget=forms.CheckboxInput(attrs={'disabled': not locs_exist})
    )
    new_location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': "Create a new location...",
            'disabled': locs_exist  # If any locations exist, disable this by default
        })
    )
