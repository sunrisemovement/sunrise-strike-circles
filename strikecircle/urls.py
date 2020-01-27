from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.conf.urls.static import static

from strikecircle.views import DataEntry, ProgramGuide, ProgressDashboard, UpdateStrikeCircle

app_name = 'strikecircle'
urlpatterns = [
    path('', ProgressDashboard.as_view(), name='dashboard'),
    path('data-entry/', DataEntry.as_view(), name='data_entry_dash'),
    path('profile/', UpdateStrikeCircle.as_view(), name='sc_edit'),
    path('program-guide/', ProgramGuide.as_view(), name='program_guide'),
]
