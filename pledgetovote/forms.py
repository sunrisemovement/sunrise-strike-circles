from django import forms

from pledgetovote.models import Address, Location, Pledge

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'

class LocationForm(forms.Form):
    locations = Location.objects.all()
    location_choices = [(loc.id, loc.name) for loc in locations]

    select_location = forms.CharField(
        required=False,
        # Hide this field if no Locations exist yet
        widget=forms.Select(choices=location_choices) if len(locations) else forms.HiddenInput()
    )
    new_location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': "Enter a location name here to create a new location"
        })
    )

class PledgeForm(forms.ModelForm):
    class Meta:
        model = Pledge
        exclude = ['address', 'location']
