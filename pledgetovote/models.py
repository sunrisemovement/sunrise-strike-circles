from django.conf import settings
from django.core.validators import EmailValidator
from django.db import models
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField


class Address(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = USStateField(max_length=2)
    zipcode = USZipCodeField(max_length=5)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.address}, {self.city} {self.state}, {self.zipcode}"


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Passcode(models.Model):
    passcode = models.CharField(max_length=50)
    active = models.BooleanField(default=False)

    def __str__(self):
        if settings.DEBUG:
            return f'<Passcode (IN DEBUG) passcode={self.passcode} active={self.active}>'
        else:
            return f'<Passcode passcode=SECRET active={self.active}>'


class Pledge(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = PhoneNumberField()
    email = models.CharField(max_length=100, validators=[EmailValidator], unique=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    picture = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
