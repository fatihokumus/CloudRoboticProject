
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^robots/iot/(?P<room_name>[^/]+)/$', consumers.IotConsumer),
]