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
from .models import StartStation
from .models import FinishStation
from .models import TransferredObject
from .models import TransferVehicle
from .models import TaskHistory

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


def gettransferredobjectlist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', TransferredObject.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)

def gettransfervehiclelist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', TransferVehicle.objects.filter(Map=map).order_by('Barcode').all())
    return JsonResponse(data, safe=False)

def gettransfervehicle(request, code):
    vehicle = TransferVehicle.objects.filter(Code=code)[0]
    data = serializers.serialize('json', vehicle)
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

def getstartstationlist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', StartStation.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)

def getfinishstationlist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', FinishStation.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)


def getgoallist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', MapGoalPoint.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)


def gettransferobjectlist(request, mapid):
    map = Map.objects.get(pk=mapid)
    data = serializers.serialize('json', TransferredObject.objects.filter(Map=map).all())
    return JsonResponse(data, safe=False)


def setrobotposition(request):
    map = Map.objects.get(pk=request.GET.get('mapid'))
    robot = Robot.objects.filter(Name=request.GET.get('robotname'), Map=map)
    robot.update(isActive = request.GET.get('isactive'), LastCoordX = request.GET.get('lastcoordx'), LastCoordY = request.GET.get('lastcoordy'))

    return JsonResponse("ok", safe=False)


def settobjectposition(request):
    map = Map.objects.get(pk=request.GET.get('mapid'))
    tobject = TransferredObject.objects.filter(Barcode=request.GET.get('name'), Map=map)
    tobject.update(isActive = request.GET.get('isactive'), LastPosX = request.GET.get('lastcoordx'), LastPosY = request.GET.get('lastcoordy'))

    return JsonResponse("ok", safe=False)


def settobjecttask(request):
    map = Map.objects.get(pk=request.GET.get('mapid'))
    tobject = TransferredObject.objects.filter(Barcode=request.GET.get('barcode'), Map=map)

    return JsonResponse("ok", safe=False)


def getmin(list, field):
    counter = -1
    minlen = 1000000
    for i in range(len(list)):
        if len(list[i][field]) < minlen:
            minlen = len(list[i][field])
            counter = i
    return counter


def allocatetasks(request, mapid):
    ppalg = request.GET.get('ppalg')
    optalg = request.GET.get('optalg')
    goals = MapGoalPoint.objects.filter(Map=map).order_by('Code').all()
    obstacles = ObstaclePoint.objects.filter(Map=map).all()
    robots = Robot.objects.filter(Map=map).order_by('Name').all()
    machines = WorkStation.objects.filter(Map=map).order_by('Code').all()
    charges = ChargingStation.objects.filter(Map=map).order_by('Code').all()
    waitings = WaitingStation.objects.filter(Map=map).order_by('Code').all()
    vehicles = TransferVehicle.objects.filter(Map=map).order_by('Barcode').all()
    tobjects = TransferredObject.objects.filter(Map=map).order_by('Barcode').all()

    #Sisteme yeni dahil olmuş kumaş var mı?
    firstTasks = TaskHistory.objects.filter(Map=map, TaskStatus=2).order_by('Barcode').all()

    # Dok arabası olmayan görev listesini al.
    for task in firstTasks:
        #Her görev için en uygun dok arabasını görevin başlangıç noktasına götürecek yeni görev oluştur.
        #Görev sırasını bir eksiği olarak alıp daha öncelikli yapıyoruz
        order = task.WorkOrder - 1
        #En yakın dok arabasını bul.
        vehicle = FindNearestVehicle(task.StartStation.CenterX, task.StartStation.CenterY)

        #Görevi oluştur. Task Statusunu WaitingTaskToExecuting (Görev İcra Edilmeyi Bekliyor) olarak belirle.
        p1 = TaskHistory(TransferredObject=task.TransferredObject, StartStation=task.StartStation, TransferVehicle = vehicle, WorkOrder=order, TaskStatus=3, isActive=True, Map=task["Map"])
        p1.save()
        #Eski görevi TaskCreated (Görev Oluşturuldu) olarak güncelle
        task.TaskStatus = 1
        task.save()

    #bekleyen görevleri listele
    waitingTasks = TaskHistory.objects.filter(Map=map, TaskStatus__in=[3,11]).order_by('Barcode').all()
    #boş robotları listele
    freeRobots = Robot.objects.filter(Map=map, isBusy=False, isActive=True).all()

    # eğer atanmamış görev sayısı birden fazlaysa optimizasyon yap
    if len(waitingTasks)>1:
        models = [];
        #Tüm görevlerin tüm boş robotlara lan uzaklıklarını hesapla
        for task in waitingTasks:
            for robot in freeRobots:
                path = getOptimumPath(robot.LastCoordX, robot.LastCoordY, task.TransferVehicle.LastPosX, task.TransferVehicle.LastPosY)
                model = {}
                model["robot"] = robot
                model["task"] = task
                model["path"] = path

        a = ['a', 'b', 'c']
        b = ['d', 'e', 'f']
        c = []
        for i in range(len(a)):
            d=[]
            for k in range(len(b)):
                d.push((a[i], b[k]))
            c.push(d)
        print(c)
           #Görevlere en yakın dok arabasını ata ve görev noktası olarak dokun konumuna güncelle. Görevin sürecini boş dok arabası iletiliyor olarak ata.
       #Görevleri listele
       #Görevi olmayan robotları getir.
       #Eğer görevi olmayan robot sayısı görev sayısından azsa kalan kısmı çalışmakta olan robotlar arasında görevi en kısa sürede bitecek olandan seç. Robotların üzerindeki görevin bitiş noktasını robotun konumu olarak al.
       #Tüm görevlerin tüm robotlara olan uzaklıklarını hesapla. Optimum toplam yol için FODPSO algoritmasını çalıştır.
       #Optimizasyon sonucuna göre robotları göreve ata ve harekete başla.
    #eğer atanmamış görev sayısı birden fazla değilse en kısa mesafedeki robotu ata ve harekete başla.

    return JsonResponse("", safe=False)



def FindNearestVehicle(mapid, finishX, finishY):
    vehicles = TransferVehicle.objects.filter(Map=map, isBusy=False).all()
    if len(vehicles) < 1:
        return None
    else:
        bestVehicle=None
        bestPath = 100000000
        for vehicle in vehicles:
            path = getOptimumPath(mapid, vehicle.LastPosX, vehicle.LastPosY, finishX, finishX)
            if path != False:
                if bestPath > len(path):
                    bestVehicle = vehicle

        return bestVehicle


def getOptimumPath(mapid, startX, startY, finishX, finishY):
    maze = getmapmaze(mapid)
    start = (startX, startY)
    end = (finishX, finishY)
    nmap = numpy.array(maze)

    path = []

    # if algo == "astar":
    path = astar(nmap, start, end)
    if path != False:
        # if algo == "astar":
        path.append(start)

    return path

def getmapmaze(mapid):
    map = Map.objects.get(pk=mapid)
    obstacles = ObstaclePoint.objects.filter(Map=map).all()
    chargingStations = ChargingStation.objects.filter(Map=map).order_by('Code').all()
    waitingStations = WaitingStation.objects.filter(Map=map).order_by('Code').all()

    width = int(map.Width / map.Distance)
    height = int(map.Height / map.Distance)
    ox = []
    oy = []


    maze = [[0 for x in range(height)] for y in range(width)]

    #Serbest olarak eklenen engelleri haritada engel noktası olarak belirle
    for i in range(len(obstacles)):
        maze[obstacles[i].CenterX][obstacles[i].CenterY] = 1
        ox.append(obstacles[i].CenterY)
        oy.append(obstacles[i].CenterX)

    #Çalışma istasyonlarını (makineleri) haritada engel noktası olarak belirle
    SetWorkStationAsObstacle(maze,map,ox,oy)

    # Bekleme istasyonlarını haritada engel noktası olarak belirle
    SetWaitingStationAsObstacle(maze,map,ox,oy)

    # Şarj istasyonlarını haritada engel noktası olarak belirle
    SetChargingStationAsObstacle(maze,map,ox,oy)

    # Başlangıç istasyonlarını haritada engel noktası olarak belirle
    SetStartStationAsObstacle(maze,map,ox,oy)

    # Teslimat istasyonlarını haritada engel noktası olarak belirle
    SetFinishStationAsObstacle(maze,map,ox,oy)

    return maze



def SetWorkStationAsObstacle(maze, map, ox, oy):
    workStations = WorkStation.objects.filter(Map=map).all()
    for workStation in len(workStations):
        position = workStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.Split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in range(len(posList)):
            if i == 0:
                points = posList[i].Split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].Split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = abs((right - left) / map.Distance)
        yc = abs((bottom - top) / map.Distance)

        for j in range(xc):
            for t in yc:
                cenX = (left + (xc * map.Distance / 2)) / map.Distance
                cenY = (top + (yc * map.Distance / 2)) / map.Distance
                maze[cenX][cenY] = 1
                ox.append(cenX)
                oy.append(cenY)



def SetWaitingStationAsObstacle(maze, map, ox, oy):
    waitingStations = WaitingStation.objects.filter(Map=map).all()
    for waitingStation in waitingStations:
        position = waitingStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.Split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in len(posList):
            if i == 0:
                points = posList[i].Split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].Split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = abs((right - left) / map.Distance)
        yc = abs((bottom - top) / map.Distance)

        for j in (xc):
            for t in yc:
                cenX = (left + (xc * map.Distance / 2)) / map.Distance
                cenY = (top + (yc * map.Distance / 2)) / map.Distance
                maze[cenX][cenY] = 1
                ox.append(cenX)
                oy.append(cenY)



def SetChargingStationAsObstacle(maze, map, ox, oy):
    chargingStations = ChargingStation.objects.filter(Map=map).all()
    for chargingStation in chargingStations:
        position = chargingStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.Split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in len(posList):
            if i == 0:
                points = posList[i].Split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].Split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = abs((right - left) / map.Distance)
        yc = abs((bottom - top) / map.Distance)

        for j in (xc):
            for t in yc:
                cenX = (left + (xc * map.Distance / 2)) / map.Distance
                cenY = (top + (yc * map.Distance / 2)) / map.Distance
                maze[cenX][cenY] = 1
                ox.append(cenX)
                oy.append(cenY)



def SetStartStationAsObstacle(maze, map, ox, oy):
    startStations = StartStation.objects.filter(Map=map).all()
    for startStation in startStations:
        position = startStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.Split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in len(posList):
            if i == 0:
                points = posList[i].Split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].Split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = abs((right - left) / map.Distance)
        yc = abs((bottom - top) / map.Distance)

        for j in (xc):
            for t in yc:
                cenX = (left + (xc * map.Distance / 2)) / map.Distance
                cenY = (top + (yc * map.Distance / 2)) / map.Distance
                maze[cenX][cenY] = 1
                ox.append(cenX)
                oy.append(cenY)




def SetFinishStationAsObstacle(maze, map, ox, oy):
    finishStations = FinishStation.objects.filter(Map=map).all()
    for finishStation in finishStations:
        position = finishStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.Split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in len(posList):
            if i == 0:
                points = posList[i].Split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].Split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = abs((right - left) / map.Distance)
        yc = abs((bottom - top) / map.Distance)

        for j in (xc):
            for t in yc:
                cenX = (left + (xc * map.Distance / 2)) / map.Distance
                cenY = (top + (yc * map.Distance / 2)) / map.Distance
                maze[cenX][cenY] = 1
                ox.append(cenX)
                oy.append(cenY)




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
            waitingS = WaitingStation(Code=point["Code"], Name=point["Name"], isActive=point["isActive"],
                                      isFull=point["isFull"], Position=point["Position"], CenterX=point["CenterX"],
                                      CenterY=point["CenterY"], Map=map)
            waitingS.save()

        ChargingStation.objects.filter(Map=map).delete()
        mapChargeStation = request.data["ChargeStationPoints"]
        for point in mapChargeStation:
            chargingS = ChargingStation(Code=point["Code"], Name=point["Name"], isActive=point["isActive"],
                                        isFull=point["isFull"], Position=point["Position"], CenterX=point["CenterX"],
                                        CenterY=point["CenterY"], Map=map)
            chargingS.save()

        StartStation.objects.filter(Map=map).delete()
        mapStartStation = request.data["StartStationPoints"]
        for point in mapStartStation:
            startS = StartStation(Code=point["Code"], Name=point["Name"], isActive=point["isActive"],
                                  isFull=point["isFull"], Position=point["Position"], CenterX=point["CenterX"],
                                  CenterY=point["CenterY"], Map=map)
            startS.save()

        FinishStation.objects.filter(Map=map).delete()
        mapFinishStation = request.data["FinishStationPoints"]
        for point in mapFinishStation:
            finishS = FinishStation(Code=point["Code"], Name=point["Name"], isActive=point["isActive"],
                                    isFull=point["isFull"], Position=point["Position"], CenterX=point["CenterX"],
                                    CenterY=point["CenterY"], Map=map)
            finishS.save()

        return Response("ok", status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def addtransferobject(request):
    if request.method == 'POST':
        map = Map.objects.get(pk=request.data["MapId"])
        startStation = StartStation.objects.get(pk=request.data["StartStationId"])
        entity = TransferredObject(Barcode=request.data["Barcode"], isActive=True, LastPosX=request.data["LastPosX"],
                                    LastPosY=request.data["LastPosY"], Length = request.data["Length"], StartStation=startStation,
                                    Map=map)
        entity.save()

        taskHistories = request.data["TaskHistories"]
        for taskHistory in taskHistories:
            workSatation = WorkStation.objects.filter(Code = taskHistory["WorkStationCode"])[0]
            startStationTask = None
            taskStatus = 1
            if taskHistory["WorkOrder"] == 1:
                taskStatus = 2
                startStationTask = startStation

            p1 = TaskHistory(TransferredObject=entity, WorkStation=workSatation, WorkOrder=taskHistory["WorkOrder"],
                             StartStation=startStationTask, TaskStatus=taskStatus, isActive=True, Map=map)
            p1.save()

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
        data["startstation"] = serializers.serialize('json', StartStation.objects.filter(Map=map).all())
        data["finishstation"] = serializers.serialize('json', FinishStation.objects.filter(Map=map).all())
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

