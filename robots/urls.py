from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<robot_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^iot/$', views.iot, name='iot'),
    url(r'^iot/(?P<room_name>[^/]+)/$', views.room, name='room'),
    url(r'^mapping/$', views.mapping, name='mapping'),
    url(r'^maplist/$', views.maplist),
    url(r'^goallist/$', views.goallist),
    url(r'^getrobotlist/(?P<mapid>[0-9]+)/$', views.getrobotlist, name='getrobotlist'),
    url(r'^getobstaclelist/(?P<mapid>[0-9]+)/$', views.getobstaclelist, name='getobstaclelist'),
    url(r'^getgoallist/(?P<mapid>[0-9]+)/$', views.getgoallist, name='getgoallist'),
]
