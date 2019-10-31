from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static


urlpatterns = [
    path('pledge-to-vote/', include('pledgetovote.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
