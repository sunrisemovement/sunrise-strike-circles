from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.conf.urls.static import static


urlpatterns = [
    path('', lambda r: redirect('pledgetovote:pledge_root')),
    path('admin/', admin.site.urls),
    path('pledge-to-vote/', include('pledgetovote.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
