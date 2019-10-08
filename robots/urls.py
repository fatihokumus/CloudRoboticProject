from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<robot_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^iot/$', views.iot, name='iot'),
    url(r'^iot/(?P<room_name>[^/]+)/$', views.room, name='room'),
    url(r'^mapping/$', views.mapping, name='mapping'),
    url(r'^maplist/$', views.maplist),
    url(r'^getmap/(?P<mapid>[0-9]+)/$', views.getmap),
    url(r'^goallist/$', views.goallist),
    url(r'^getrobotlist/(?P<mapid>[0-9]+)/$', views.getrobotlist, name='getrobotlist'),
    url(r'^gettransferredobjectlist/(?P<mapid>[0-9]+)/$', views.gettransferredobjectlist, name='gettransferredobjectlist'),
    url(r'^gettransfervehiclelist/(?P<mapid>[0-9]+)/$', views.gettransfervehiclelist, name='gettransfervehiclelist'),
    url(r'^getobstaclelist/(?P<mapid>[0-9]+)/$', views.getobstaclelist, name='getobstaclelist'),
    url(r'^getworkstationlist/(?P<mapid>[0-9]+)/$', views.getworkstationlist, name='getworkstationlist'),
    url(r'^getwaitingstationlist/(?P<mapid>[0-9]+)/$', views.getwaitingstationlist, name='getwaitingstationlist'),
    url(r'^getchargingstationlist/(?P<mapid>[0-9]+)/$', views.getchargingstationlist, name='getchargingstationlist'),
    url(r'^getstartstationlist/(?P<mapid>[0-9]+)/$', views.getstartstationlist, name='getstartstationlist'),
    url(r'^getfinishstationlist/(?P<mapid>[0-9]+)/$', views.getfinishstationlist, name='getfinishstationlist'),
    url(r'^getgoallist/(?P<mapid>[0-9]+)/$', views.getgoallist, name='getgoallist'),
    url(r'^getpathplan/(?P<mapid>[0-9]+)/$', views.getpathplan, name='getpathplan'),
    url(r'^setrobotposition/$', views.setrobotposition, name='setrobotposition'),
]
