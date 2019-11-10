from django.contrib import admin
from pledgetovote.models import Address, Location, Passcode, Pledge

admin.site.register(Address)
admin.site.register(Location)
admin.site.register(Pledge)
admin.site.register(Passcode)
