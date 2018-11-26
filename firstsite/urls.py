
from django.contrib import admin
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^robots/', include('robots.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Teleport"
admin.site.site_title = "Teleport Project Admin Portal"
admin.site.index_title = "Endüstriyel Bina İçi Lojistik Otonom Robot Sistemi"
