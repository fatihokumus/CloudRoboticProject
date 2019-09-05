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
from .models import ObstaclePoint
from .models import WorkStation
from .models import MapGoalPoint
from .models import ChargingStation
from .models import WaitingStation
from .PathPlanning.AStar.a_star import astar
from .PathPlanning.Dijkstra.dijkstra import dijkstras
from .PathPlanning.PotentialFieldPlanning.potential_field_planning import potential_field_planning

import json
import numpy

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
    data = serializers.serialize('json', ObstaclePoint.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)

def getworkstationlist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', WorkStation.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)

def getwaitingstationlist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', WaitingStation.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)

def getchargingstationlist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', ChargingStation.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)

def getgoallist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', MapGoalPoint.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)


def setrobotposition(request):
    map = Map.objects.get(pk=request.GET.get('mapid'))
    robot = Robot.objects.filter(Name=request.GET.get('robotname'), Map=map)
    robot.update(isActive = request.GET.get('isactive'), LastCoordX = request.GET.get('lastcoordx'), LastCoordY = request.GET.get('lastcoordy'))

    return JsonResponse("ok", safe=False)


def getmin(list, field):
    counter = -1
    minlen = 1000000
    for i in range(len(list)):
        if len(list[i][field]) < minlen:
            minlen = len(list[i][field])
            counter = i
    return counter


def getpathplan(request, mapid):
    algo = request.GET.get('algo')
    map = Map.objects.get(pk=mapid)
    goals = MapGoalPoint.objects.filter(Map=map).order_by('Code').all()
    obstacles = ObstaclePoint.objects.filter(Map=map).all()
    robots = Robot.objects.filter(Map=map).order_by('Name').all()

    models=[]
    tasks = []

    #TODO: görevler veritabanından gelecek
    for r in range(len(robots)):
        task = {}
        task["robot"]= robots[r]
        task["goals"]= []
        tasks.append(task);

    for g in range(len(goals)):
        rob = getmin(tasks, "goals")

        if len(tasks[rob]["goals"])> 0:
            sx = int(tasks[rob]["goals"][len(tasks[rob]["goals"]) - 1].Left / map.Distance)
            sy = int(tasks[rob]["goals"][len(tasks[rob]["goals"]) - 1].Top / map.Distance)
        else:
            sx = int(tasks[rob]["robot"].LastCoordX/map.Distance)
            sy = int(tasks[rob]["robot"].LastCoordY/map.Distance)

        gx = int(goals[g].Left/map.Distance)
        gy = int(goals[g].Top/map.Distance)
        width = int(map.Width/map.Distance)
        height = int(map.Height/map.Distance)

        tasks[rob]["goals"].append(goals[g])

        maze = [[0 for x in range(height)] for y in range(width)]

        ox = []
        oy = []

        for i in range(len(obstacles)):
            maze[obstacles[i].CenterX][obstacles[i].CenterY] = 1
            ox.append(obstacles[i].CenterY)
            oy.append(obstacles[i].CenterX)

        start = (sx, sy)
        end = (gx, gy)
        nmap = numpy.array(maze)

        path = []
        if algo == "astar":
            path = astar(nmap, start, end)
        elif algo == "dijkstra":
            #grid_size = 1.0  # [m]
            #robot_size = 1.0  # [m]
            #rx, ry = dijkstra_planning(sx, sy, gx, gy, ox, oy, grid_size, robot_size)
            npstart = numpy.array([[sx], [sy], [1.5707963267948966]])
            npgoal = numpy.array([[gx], [gy], [-1.5707963267948966]])
            x_spacing2 = 1
            y_spacing2 = 1
            path2 = dijkstras(nmap, x_spacing2, y_spacing2, npstart, npgoal).tolist()

            for ii in range(len(path2)):
                path.append((int(path2[ii][0]), int(path2[ii][1])))
        elif algo == "apf":

            grid_size = 1
            robot_radius = 1 #

            rx, ry = potential_field_planning(
                sx, sy, gx, gy, ox, oy, grid_size, robot_radius)



        if path != False:
            if algo == "astar":
                path.append(start)
            model = {}
            model["robot"] = tasks[rob]["robot"].Name
            model["goal"] = goals[g].Code
            model["path"] = path
            models.append(model)

    return JsonResponse(models, safe=False)


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

        ObstaclePoint.objects.filter(Map = map).delete()
        mapObstacle = request.data["ObstaclePoints"]
        for point in mapObstacle:
            p1 = ObstaclePoint(Left = point["Left"], Right = point["Right"], Top = point["Top"], Bottom = point["Bottom"], CenterX = point["CenterX"], CenterY = point["CenterY"], Map = map)
            p1.save()

        WorkStation.objects.filter(Map=map).delete()
        mapWorkStation = request.data["WorkStationPoints"]
        for point in mapWorkStation:
            workS = WorkStation(Code=point["Code"], Name=point["Name"], isActive=point["isActive"], Position=point["Position"], EnterPosX=point["EnterPosX"], EnterPosY=point["EnterPosY"], ExitPosX=point["ExitPosX"], ExitPosY=point["ExitPosY"], Map=map)
            workS.save()

        WaitingStation.objects.filter(Map=map).delete()
        mapWaitingStation = request.data["WaitingStationPoints"]
        for point in mapWaitingStation:
            waitingS = WaitingStation(Code=point["Code"], Name=point["Name"], isActive=point["isActive"], isFull=point["isFull"], Position=point["Position"], CenterX=point["CenterX"], CenterY=point["CenterY"], Map=map)
            waitingS.save()

        ChargingStation.objects.filter(Map=map).delete()
        mapChargeStation = request.data["ChargeStationPoints"]
        for point in mapChargeStation:
            chargingS = ChargingStation(Code=point["Code"], Name=point["Name"], isActive=point["isActive"], isFull=point["isFull"], Position=point["Position"], CenterX=point["CenterX"], CenterY=point["CenterY"], Map=map)
            chargingS.save()

        return Response("ok", status=status.HTTP_200_OK)


@api_view(['GET'])
def getmap(request, mapid):
    if request.method == 'GET':
        map = Map.objects.get(pk=mapid)
        data = {}
        data["obstacle"] = serializers.serialize('json', ObstaclePoint.objects.filter(Map=map).all())
        data["workstation"] = serializers.serialize('json', WorkStation.objects.filter(Map=map).all())
        data["waitingstation"] = serializers.serialize('json', WaitingStation.objects.filter(Map=map).all())
        data["chargingstation"] = serializers.serialize('json', ChargingStation.objects.filter(Map=map).all())
        return Response(data)


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

