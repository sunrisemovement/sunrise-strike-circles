from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.conf.urls.static import static

from strikecircle.views import DataInput, ProgramGuide, ProgressDashboard, UpdateStrikeCircle

app_name = 'strikecircle'
urlpatterns = [
    path('', ProgressDashboard.as_view(), name='dashboard'),
    path('data-entry/', DataInput.as_view(), name='data_input_dash'),
    path('profile/', UpdateStrikeCircle.as_view(), name='sc_edit'),
    path('program-guide/', ProgramGuide.as_view(), name='program_guide'),
]
