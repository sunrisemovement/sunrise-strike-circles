from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.conf.urls.static import static

from pledgetovote.views import Dashboard, DataEntry, Signup, UpdateStrikeCircle, CreatePledge, PledgeList, UpdatePledge

app_name = 'pledgetovote'
urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('data-entry/', DataEntry.as_view(), name='data_entry_dash'),
    path('profile/', UpdateStrikeCircle.as_view(), name='sc_edit'),
    path('pledge/new/', CreatePledge.as_view(), name='pledge_new'),
    path('pledge/<int:pk>/', UpdatePledge.as_view(), name='pledge_edit'),
    path('signup/', Signup.as_view(), name='signup')
]
