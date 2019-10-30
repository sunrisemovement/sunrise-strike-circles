from django.core.validators import EmailValidator
from django.db import models
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField


class Address(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = USStateField(max_length=2)
    zipcode = USZipCodeField(max_length=5)

    def __str__(self):
        return f"{address}, {city} {state}, {zipcode}"


class Pledger(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = PhoneNumberField()
    email = models.CharField(max_length=100, validators=[EmailValidator], unique=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    picture = models.ImageField(upload_to='uploads/%Y/%m/%d/')

    def __str__(self):
        return f"{first_name} {last_name} ({email})"
