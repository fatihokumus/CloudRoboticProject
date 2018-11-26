from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<robot_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^iot/$', views.iot, name='iot'),
    url(r'^iot/(?P<room_name>[^/]+)/$', views.room, name='room'),
    url(r'^mapping/$', views.mapping, name='mapping'),
]
