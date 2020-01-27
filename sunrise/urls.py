from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.conf.urls.static import static

from strikecircle.views import Signup

urlpatterns = [
    path('', lambda r: redirect('strikecircle:dashboard')),
    path('admin/', admin.site.urls),
    path('strike-circle/', include('strikecircle.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('users/signup/', Signup.as_view(), name='signup')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
