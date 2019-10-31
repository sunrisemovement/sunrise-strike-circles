from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.conf.urls.static import static

from pledgetovote.views import CreatePledge, reroute, SetLocation, UpdatePledge

app_name = 'pledgetovote'
urlpatterns = [
    path('', reroute, name='pledge_root'),
    path('pledge/new/', CreatePledge.as_view(), name='pledge_new'),
    path('pledge/<int:pk>/', UpdatePledge.as_view(), name='pledge_edit'),
    path('set-location/', SetLocation.as_view(), name='set_location')
]
