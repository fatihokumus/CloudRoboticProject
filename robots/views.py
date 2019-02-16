from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.utils.safestring import mark_safe
from django.core import serializers

from .models import Robot
from .models import Map
from .models import MapObstaclePoint
from .models import MapGoalPoint

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
    context = {'robot' : robot}
    return HttpResponse(render(request, 'robot/detail.html', context))

def iot(request):
    try:
        mapList = Map.objects.all()
    except Robot.DoesNotExist:
        raise Http404("Kayıt Bulunamadı")
    context = {'MapList' : mapList}
    return HttpResponse(render(request, 'iot/index.html', context))


def getrobotlist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', Robot.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)


def getobstaclelist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', MapObstaclePoint.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)

def getgoallist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', MapGoalPoint.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)


def mapping(request):
    return HttpResponse(render(request, 'robot/mapping.html'))


def room(request, room_name):
    return render(request, 'iot/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })


@api_view(['GET', 'POST'])
def maplist(request):
    if request.method == 'GET':
        data = serializers.serialize('json', Map.objects.all())
        return Response(data)

    elif request.method == 'POST':
        map = Map.objects.get(pk=request.data["MapId"])
        map.Height = request.data["Height"]
        map.Width = request.data["Width"]
        map.Distance = request.data["Distance"]
        map.save()

        MapObstaclePoint.objects.filter(Map = map).delete()
        gridMap = request.data["ObstaclePoints"]
        for point in gridMap:
            p1 = MapObstaclePoint(Left = point["Left"], Right = point["Right"], Top = point["Top"], Bottom = point["Bottom"], Map = map)
            p1.save()

        return Response("ok", status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def goallist(request):
    if request.method == 'POST':
        map = Map.objects.get(pk=request.data["MapId"])

        MapGoalPoint.objects.filter(Map = map).delete()
        goalMap = request.data["GoalPoints"]
        for point in goalMap:
            p1 = MapGoalPoint(Code = point["Code"], Left = point["Left"], Right = point["Right"], Top = point["Top"], Bottom = point["Bottom"], Map = map)
            p1.save()

        return Response("ok", status=status.HTTP_200_OK)

