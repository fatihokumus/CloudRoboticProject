from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render

from django.utils.safestring import mark_safe

from .models import Robot
import json

def index(request):
    all_robots = Robot.objects.all()
    context = {'all_robots' : all_robots,}
    return HttpResponse(render(request,'robot/index.html', context))


def detail(request, robot_id):
    try:
        robot = Robot.objects.get(pk=robot_id)
    except Robot.DoesNotExist:
        raise Http404("Kayıt Bulunamadı")
    context = {'robot' : robot,}
    return HttpResponse(render(request, 'robot/detail.html', context))

def iot(request):
    return HttpResponse(render(request, 'iot/index.html'))

def mapping(request):
    return HttpResponse(render(request, 'robot/mapping.html'))

def room(request, room_name):
    return render(request, 'iot/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })

