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
from .models import RobotTaskHistory
from .models import RobotTaskHistoryLog

from .PathPlanning.AStar.a_star import astar
from .PathPlanning.Dijkstra.dijkstra import dijkstras
from .PathPlanning.PotentialFieldPlanning.potential_field_planning import potential_field_planning
from pydstarlite import dstarlite, grid, utility

import json
import numpy
import math
import datetime

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
    robot = Robot.objects.get(Code=request.GET.get('robotname'), Map=map)
    robot.isActive = request.GET.get('isactive')
    robot.LastCoordX = request.GET.get('lastcoordx')
    robot.LastCoordY = request.GET.get('lastcoordy')
    robot.save()
    model ={}
    if robot.isBusy == True:
        rtask = RobotTaskHistory.objects.filter(Robot=robot, RobotStatus__lt=3).order_by('id').all()
        if rtask != None:
            if rtask[0].TaskHistory.TransferVehicle != None and rtask[0].TaskHistory.TaskStatus == 5:
                rtask[0].TaskHistory.TransferVehicle.LastPosX = request.GET.get('lastcoordx')
                rtask[0].TaskHistory.TransferVehicle.LastPosY = request.GET.get('lastcoordy')
                rtask[0].TaskHistory.TransferVehicle.save()
                model["vehicle"] = rtask[0].TaskHistory.TransferVehicle.Barcode
            else:
                model["vehicle"] = ""

            if rtask[0].TaskHistory.TransferredObject != None and rtask[0].TaskHistory.TaskStatus == 5:
                rtask[0].TaskHistory.TransferredObject.LastPosX = request.GET.get('lastcoordx')
                rtask[0].TaskHistory.TransferredObject.LastPosY = request.GET.get('lastcoordy')
                rtask[0].TaskHistory.TransferredObject.save()
                model["object"] = rtask[0].TaskHistory.TransferredObject.Barcode
            else:
                model["object"] = ""
        else:
            model["vehicle"] = ""
            model["object"] = ""
    else:
        model["vehicle"] = ""
        model["object"] = ""


    return JsonResponse(model, safe=False)

def skiptonextjob(request):
    map = Map.objects.get(pk=request.GET.get('mapid'))
    robot = Robot.objects.get(Code=request.GET.get('robotname'), Map=map)

    #Robotun hareket halinde olduğu task history'yi getir. Eğer 3'ün altındaysa hareket halindedir. Eğer 3'se işlem tamamlanmış demektir.
    rth = RobotTaskHistory.objects.filter(Robot = robot, RobotStatus__lt = 3).all()
    #History'nin statusunu bir artır.
    retlist = []
    if rth != None:
        robotTaskHistory = rth[0]


        robotTaskHistory.RobotStatus = robotTaskHistory.RobotStatus + 1
        robotTaskHistory.save()

        t1 = RobotTaskHistoryLog(RobotTaskHistory=robotTaskHistory, RobotStatus=robotTaskHistory.RobotStatus, LogTime=datetime.datetime.now())
        t1.save()

        #ÜstTaskHistorynin statusunu 1 artır.
        stat = robotTaskHistory.TaskHistory.TaskStatus + 1
        #if taskHistory != None:
        #    #Eğer görevin Start istasyonu dolu ama bir sonraki görevin Start istasyonu dolu değilse bu başlangıç noktasında demektir. Bu durumda 004-RobotMovingToVehicle adımı atlanır
        #    if robotTaskHistory.TaskHistory.StartStation != None and taskHistory.StartStation == None and stat == 4:
        #        stat = stat + 1
        #else:
        #    # Teslimat noktasına gidecek demektir.
        #    if stat == 4:
        #        stat = stat + 1
        #    #Teslimat noktası ataması burada yapılacak.

        robotTaskHistory.TaskHistory.TaskStatus = stat
        robotTaskHistory.TaskHistory.save()

        if robotTaskHistory.RobotStatus < 3:
            #Robot dok arabasını görev yerine götürüyorsa yol çiz ve robota emir olarak gönder.
            path = []
            if robotTaskHistory.TaskHistory.TaskStatus == 5:
                if robotTaskHistory.TaskHistory.isExitTask == False:
                    path = getOptimumPath(map, robot.LastCoordX, robot.LastCoordY, robotTaskHistory.TaskHistory.TransferredObject.LastPosX,
                                  robotTaskHistory.TaskHistory.TransferredObject.LastPosY)
                else:
                    path = getOptimumPath(map, robot.LastCoordX, robot.LastCoordY,
                                          robotTaskHistory.TaskHistory.WorkStation.ExitPosX,
                                          robotTaskHistory.TaskHistory.WorkStation.ExitPosY)
            ret = {}
            ret["robot"] = robot.Code
            ret["task"] = robotTaskHistory.TaskHistory.pk
            ret["path"] = path
            retlist.append(ret)
        #TODO:makinenin çıkış noktasına gitmek için bir iş daha oluşturulmayacak.
        #  robotTaskHistory.TaskHistory.TaskStatus = 6 ise görev tamamlanmış demektir. Aynı ürünün bir sonraki işine geçilir. Bir sonraki işi aktifleştirmek için TaskStatus alanı 3 (WaitingTaskToExecuting) yapılır.
        if robotTaskHistory.TaskHistory.TaskStatus == 6:
            if robotTaskHistory.TaskHistory.isExitTask == True:
                taskHistory = TaskHistory.objects.filter(
                    TransferredObject=robotTaskHistory.TaskHistory.TransferredObject,
                    WorkOrder=(robotTaskHistory.TaskHistory.WorkOrder), isExitTask = True, TaskStatus__lt=3)
            else:
                taskHistory = TaskHistory.objects.filter(
                    TransferredObject=robotTaskHistory.TaskHistory.TransferredObject,
                    WorkOrder=(robotTaskHistory.TaskHistory.WorkOrder + 1))

            if taskHistory != None:
                # Eğer Start istasyonu varsa bu ilk görevdir. Bu görev aynı dok aracı ile ifa edilir.
                for thist in taskHistory:
                    if robotTaskHistory.TaskHistory.StartStation != None and thist.isExitTask == False:
                        thist.TransferVehicle = robotTaskHistory.TaskHistory.TransferVehicle
                    thist.TaskStatus = 3
                    thist.WorkTime = datetime.datetime.now() + datetime.timedelta(seconds=10)
                    thist.save()

        #Robotu özgürleştir.
        robot.isBusy=False
        robot.save()
        #TODO: robotu en yakın şarj istasyonuna gönder.

    return JsonResponse(retlist, safe=False)


def settobjectposition(request):
    map = Map.objects.get(pk=request.GET.get('mapid'))
    tobject = TransferVehicle.objects.get(Barcode = request.GET.get('name'), Map=map)
    tobject.isActive = request.GET.get('isactive')
    tobject.LastPosX = request.GET.get('lastcoordx')
    tobject.LastPosY = request.GET.get('lastcoordy')
    tobject.save()

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


def getOptimumPath(map, startX, startY, finishX, finishY):
    sx= int(startX / map.Distance)
    sy = int(startY / map.Distance)
    fx = int(finishX / map.Distance)
    fy = int(finishY / map.Distance)
    maze, obstList = getmapmaze(map)
    maze[sx][sy] = 'A'
    maze[fx][fy] = 'Z'
    #start = (sx, sy)
    #end = (fx, fy)
    #nmap = numpy.array(maze)

    #path = []

    # if algo == "astar":
    #path = astar(nmap, start, end)

    #grid_size = 1
    #robot_radius = 1  #
    nmap = ""
    for row in maze[:]:
        srow = ""
        for col in row:
            srow = srow + col

        nmap = nmap  + srow + "\n"




    GRAPH, START, END = utility.grid_from_string(nmap)
    dstar = dstarlite.DStarLite(GRAPH, START, END)
    path = [p for p, o, w in dstar.move_to_goal()]

    #if path != False:
        # if algo == "astar":
    #    path.append(start)

    return path


def SetWorkStationAsObstacle(maze, map, obstList):
    workStations = WorkStation.objects.filter(Map=map).all()
    for workStation in workStations:
        position = workStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in range(len(posList)):
            if i == 0:
                points = posList[i].split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = int(abs((right - left) / map.Distance))
        yc = int(abs((bottom - top) / map.Distance))

        for j in range(xc):
            for t in range(yc):
                cenX = int((left + (j * map.Distance)) / map.Distance)
                cenY = int((top + (t* map.Distance)) / map.Distance)
                maze[cenX][cenY] = '#'
                obstList.add((cenY, cenX))


def SetWaitingStationAsObstacle(maze, map, obstList):
    waitingStations = WaitingStation.objects.filter(Map=map).all()
    for waitingStation in waitingStations:
        position = waitingStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in range(len(posList)):
            if i == 0:
                points = posList[i].split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = int(abs((right - left) / map.Distance))
        yc = int(abs((bottom - top) / map.Distance))

        for j in range(xc):
            for t in range(yc):
                cenX = int((left + (j * map.Distance)) / map.Distance)
                cenY = int((top + (t * map.Distance)) / map.Distance)
                maze[cenX][cenY] = '#'
                obstList.add((cenY,cenX))


def SetChargingStationAsObstacle(maze, map, obstList):
    chargingStations = ChargingStation.objects.filter(Map=map).all()
    for chargingStation in chargingStations:
        position = chargingStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in range(len(posList)):
            if i == 0:
                points = posList[i].split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = int(abs((right - left) / map.Distance))
        yc = int(abs((bottom - top) / map.Distance))

        for j in range(xc):
            for t in range(yc):
                cenX = int((left + (j * map.Distance)) / map.Distance)
                cenY = int((top + (t * map.Distance)) / map.Distance)
                maze[cenX][cenY] = '#'
                obstList.add((cenY,cenX))


def SetStartStationAsObstacle(maze, map, obstList):
    startStations = StartStation.objects.filter(Map=map).all()
    for startStation in startStations:
        position = startStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in range(len(posList)):
            if i == 0:
                points = posList[i].split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = int(abs((right - left) / map.Distance))
        yc = int(abs((bottom - top) / map.Distance))

        for j in range(xc):
            for t in range(yc):
                cenX = int((left + (j * map.Distance)) / map.Distance)
                cenY = int((top + (t * map.Distance)) / map.Distance)
                maze[cenX][cenY] = '#'
                obstList.add((cenY,cenX))


def SetFinishStationAsObstacle(maze, map, obstList):
    finishStations = FinishStation.objects.filter(Map=map).all()
    for finishStation in finishStations:
        position = finishStation.Position;
        position = position.replace("[", "").replace("]", "").replace("},", " ").replace("{", "").replace("}", "");

        posList = position.split(' ')
        left = 0
        top = 0
        right = 0
        bottom = 0
        for i in range(len(posList)):
            if i == 0:
                points = posList[i].split(',')
                left = int(points[0])
                top = int(points[1])
            elif i == 2:
                points = posList[i].split(',')
                right = int(points[0])
                bottom = int(points[1])

        xc = int(abs((right - left) / map.Distance))
        yc = int(abs((bottom - top) / map.Distance))

        for j in range(xc):
            for t in range(yc):
                cenX = int((left + (j * map.Distance)) / map.Distance)
                cenY = int((top + (t * map.Distance)) / map.Distance)
                maze[cenX][cenY] = '#'
                obstList.add((cenY,cenX))


def getmapmaze(map):

    obstacles = ObstaclePoint.objects.filter(Map=map).all()

    width = int(map.Width / map.Distance)
    height = int(map.Height / map.Distance)
    obstList=set()


    maze = [['.' for x in range(height)] for y in range(width)]

    #Serbest olarak eklenen engelleri haritada engel noktası olarak belirle
    for i in range(len(obstacles)):
        maze[obstacles[i].CenterX][obstacles[i].CenterY] = '#'
        obstList.add((obstacles[i].CenterY,obstacles[i].CenterX))

    #Çalışma istasyonlarını (makineleri) haritada engel noktası olarak belirle
    SetWorkStationAsObstacle(maze,map,obstList)

    # Bekleme istasyonlarını haritada engel noktası olarak belirle
    SetWaitingStationAsObstacle(maze,map,obstList)

    # Şarj istasyonlarını haritada engel noktası olarak belirle
    SetChargingStationAsObstacle(maze,map,obstList)

    # Başlangıç istasyonlarını haritada engel noktası olarak belirle
    SetStartStationAsObstacle(maze,map,obstList)

    # Teslimat istasyonlarını haritada engel noktası olarak belirle
    SetFinishStationAsObstacle(maze,map,obstList)

    return maze, obstList


def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def getoptimumallocation(list):
    robots = unique([d['robot'] for d in list])
    goals = unique([d['goal'] for d in list])
    # kombinasyon matrisi
    combin = []

    # hangi dizi daha az ise o kadar atama yapılacağı için aşağıdaki temp değişkenler kullanılacak.
    temp1 = []
    temp2 = []

    # Atama sayısı gruplardaki en az sayı kimdesyse o kadar olacağı için ayarlama yaptık
    if len(robots) > len(goals):
        temp1 = goals
        temp2 = robots
    else:
        temp1 = robots
        temp2 = goals

    # İlk olarak kombinasyon matrisi oluşturulur.
    for i in range(len(temp1)):
        row = []
        for k in range(len(temp2)):
            row.append((temp1[i], temp2[k]))
        combin.append(row)

    # kaç sütunlu
    width = len(combin[:])

    # kaç satırlı
    height = len(combin[0][:])

    # Öncelikle Olasılık Matrisi oluşturulur. matrisin n x m boyutundadır. r=robot sayısı h=hedef saysı olarak alırsak;
    # eğer r < h is n=h^r ve m=r olur.
    # eğer r > h is n=r^h ve m=h olur.
    # eğer r = h is n=r^r ve m=r olur.

    # Olasılık matrisi kaç satırlı olacak
    l = int(math.pow(height, width - 1))

    # Olasılık matrisini oluştur. İlk sütun değerlerini ata. diğer sütunlara 1 ata.
    prob = []
    for i in range(height):
        for j in range(l):
            row = []
            row.append(combin[0][i])
            for k in range(width - 1):
                row.append('1')
            prob.append(row)

    # Olasılık matrisinin diğer sütunlarının verilerini ata.
    for i in range(width - 1):
        col = i + 1
        m = int(math.pow(height, width - 1 - col))
        row = 0
        for k in range(int(len(prob) / m)):
            for ss in range(m):
                prob[row][col] = combin[col][k % height]
                row = row + 1

    #1. kısıtımız bir hedefe sadece 1 robot ve bir robota sadece 1 hedef atanabilir. Bu kısıta uymayan kayıtlar listeden çıkarılır.
    num = 0
    for row in range(len(prob)):
        row = prob[num]
        comp = False
        for col in row:
            el = [x for x in row if x[1] == col[1]]
            if (len(el) > 1):
                comp = True
        if comp == True:
            prob.remove(row)
            num = num - 1
        num = num + 1

    #maliyeti en düşük olan satırı seç
    currentrow = []
    cost = 100000000
    for row in prob:
        sumPath = 0
        models = []
        for col in row:
            model = {}
            if len(robots) > len(goals):
                goal = col[0]
                robot = col[1]
            else:
                goal = col[1]
                robot = col[0]
            el = [x for x in list if x["robot"] == robot and x["goal"] == goal][0]
            sumPath = sumPath + int(el["pathlength"])
            model["robot"] = robot
            model["goal"] = goal
            models.append(model)
            # 2. kısıt: en az maliyetli olan satırda atanan göreve robotun enerjisi yetmeyecekse satır listeden  çıkarılır.
            #if int(el["power"]) > int(el["path"]):
            #    sum = 100000000

        if sumPath < cost:
            cost = sumPath
            currentrow = models

    return currentrow


def FindNearestVehicle(map, finishX, finishY):
    vehicles = TransferVehicle.objects.filter(Map=map, isBusy=False, isActive = True).all()
    if len(vehicles) < 1:
        return None
    else:
        bestVehicle=None
        bestPath = 100000000
        for vehicle in vehicles:
            path = getOptimumPath(map, vehicle.LastPosX, vehicle.LastPosY, finishX, finishY)
            if bestPath > len(path):
                bestVehicle = vehicle
                bestPath = len(path)

        return bestVehicle


def resetmap(request, mapid):
    map = Map.objects.get(pk=mapid)
    TransferredObject.objects.filter(Map = map).delete()
    TransferVehicle.objects.filter(Map = map).update(isBusy = False, isActive=False, LastPosX=0, LastPosY=0)
    Robot.objects.filter(Map=map).update(isBusy=False, isActive=False, LastCoordX=0, LastCoordY=0)

    return JsonResponse("", safe=False)


def allocatetasks(request, mapid):
    ppalg = request.GET.get('ppalg')
    optalg = request.GET.get('optalg')
    map = Map.objects.get(pk=mapid)

    #Sisteme yeni dahil olmuş kumaş var mı?
    firstTasks = TaskHistory.objects.filter(Map=map, TaskStatus = 2).order_by('TaskStatus').all()

    # Dok arabası olmayan görev listesini al.
    for task in firstTasks:
        #Her görev için en uygun dok arabasını görevin başlangıç noktasına götürecek yeni görev oluştur.

        order = task.WorkOrder
        #Görev sırasını bir eksiği olarak alıp daha öncelikli yapıyoruz. Eğer makine çıkış noktası ise öncelik aynı kalıyor
        if task.isExitTask == False:
            order = task.WorkOrder - 1
        #En yakın dok arabasını bul.
        if task.StartStation != None:
            vehicle = FindNearestVehicle(map, task.StartStation.CenterX, task.StartStation.CenterY)
        else:
            vehicle = FindNearestVehicle(map, task.WorkStation.ExitPosX, task.WorkStation.ExitPosY)

        #Görevi oluştur. Task Statusunu WaitingTaskToExecuting (Görev İcra Edilmeyi Bekliyor) olarak belirle.
        p1 = TaskHistory(TransferredObject=task.TransferredObject, StartStation=task.StartStation, WorkOrder=order,
                         TransferVehicle=vehicle, TaskStatus=3, WorkTime = datetime.datetime.now(), isTaskGoingToVehicle=True, isActive=True, Map= task.Map)
        p1.save()
        vehicle.isBusy = True
        vehicle.save()
        #Eski görevi TaskCreated (Görev Oluşturuldu) olarak güncelle
        task.TaskStatus = 1
        task.TransferVehicle = vehicle
        task.save()

    exitTasks = TaskHistory.objects.filter(Map=map, TaskStatus=3, isExitTask = True).order_by('TaskStatus').all()
    for etask in exitTasks:
        if etask.TransferVehicle == None:
            otherTask = TaskHistory.objects.get(TransferredObject=etask.TransferredObject, isExitTask=False, WorkOrder=etask.WorkOrder)
            order = etask.WorkOrder
            vehicle = FindNearestVehicle(map, etask.WorkStation.ExitPosX, etask.WorkStation.ExitPosY)
            etask.TransferVehicle = vehicle
            etask.save()
            # Makinenin çıkışına gidecek dok arabasını seçen ve uygulayan görevi oluştur. Task Statusunu WaitingTaskToExecuting (Görev İcra Edilmeyi Bekliyor) olarak belirle.
            p2 = TaskHistory(TransferredObject=etask.TransferredObject, StartStation=etask.StartStation, WorkOrder=order,
                             TransferVehicle=vehicle, TaskStatus=3, isTaskGoingToVehicle=True, isExitTask=True, WorkTime=otherTask.WorkTime, isActive=True,
                             Map=etask.Map)
            p2.save()
            vehicle.isBusy = True
            vehicle.save()
            # Eski görevi TaskCreated (Görev Oluşturuldu) olarak güncelle
            etask.TaskStatus = 1
            etask.TransferVehicle = vehicle
            etask.save()

    #bekleyen görevleri listele
    waitingTasks = TaskHistory.objects.filter(Map=map, TaskStatus = 3, WorkTime__lte=datetime.datetime.now()).order_by('TaskStatus').all()
    #boş robotları listele
    freeRobots = Robot.objects.filter(Map=map, isBusy=False, isActive=True).order_by('Code').all()

    returnlist = []
    # eğer atanmamış görev sayısı birden fazlaysa optimizasyon yap
    if len(waitingTasks)>=1:
        models = []
        list = []
        #Tüm görevlerin tüm boş robotlara lan uzaklıklarını hesapla
        for task in waitingTasks:
            for robot in freeRobots:
                if task.isExitTask == True and task.TransferVehicle == None:
                    vehicle = FindNearestVehicle(map, task.WorkStation.ExitPosX, task.WorkStation.ExitPosY)
                    task.TransferVehicle = vehicle
                    task.save()

                if robot.LastCoordX == task.TransferVehicle.LastPosX and robot.LastCoordY == task.TransferVehicle.LastPosY:
                    model = {}
                    model["robot"] = robot
                    model["task"] = task.pk
                    model["path"] = []
                    model["pathlength"] = 0
                    models.append(model)
                    elm = {}
                    elm["robot"] = robot.Code
                    elm["goal"] = task.pk
                    elm["pathlength"] = 0
                    list.append(elm)
                else:
                    if task.isTaskGoingToVehicle == False:
                        path = getOptimumPath(map, robot.LastCoordX, robot.LastCoordY, task.WorkStation.EnterPosX,
                                              task.WorkStation.EnterPosY)
                        model = {}
                        model["robot"] = robot.Code
                        model["task"] = task.pk
                        model["path"] = path
                        model["pathlength"] = len(path)
                        models.append(model)
                        elm = {}
                        elm["robot"] = robot.Code
                        elm["goal"] = task.pk
                        elm["pathlength"] = len(path)
                        list.append(elm)
                    else:
                        #doka ulaşma görevidir
                        path = getOptimumPath(map, robot.LastCoordX, robot.LastCoordY, task.TransferVehicle.LastPosX,
                                              task.TransferVehicle.LastPosY)
                        model = {}
                        model["robot"] = robot.Code
                        model["task"] = task.pk
                        model["path"] = path
                        model["pathlength"] = len(path)
                        models.append(model)
                        elm = {}
                        elm["robot"] = robot.Code
                        elm["goal"] = task.pk
                        elm["pathlength"] = len(path)
                        list.append(elm)


        optlist = getoptimumallocation(list)
        returnlist = []
        for col in optlist:
            el = [x for x in models if x["robot"] == col["robot"] and x["task"] == col["goal"]][0]
            ret = {}
            ret["robot"] = el["robot"]
            ret["task"]  = el["task"]
            ret["path"]  = el["path"]
            taskHistory = TaskHistory.objects.get(pk=int(el["task"]))
            robot = Robot.objects.get(Map = map, Code=el["robot"])
            taskHistory.Robot = robot
            taskHistoryNext = TaskHistory.objects.filter(TransferredObject=taskHistory.TransferredObject,
                                                  WorkOrder=(taskHistory.WorkOrder + 1))
            if taskHistoryNext != None:
                for thNext in taskHistoryNext:
                    #Eğer bir sonraki görevin Start istasyonu dolu değilse bu ilk görev değil demektir. Bu durumda 004-RobotMovingToVehicle adımı atlanır
                    if thNext.StartStation == None:
                        #Başka bir dok arabasını makinenin çıkış noktasına yönlendir.
                        taskHistory.TaskStatus = 5
                    else:
                        taskHistory.TaskStatus = 4
            else:
                # Teslimat noktasına gidecek demektir.
                taskHistory.TaskStatus = 5
                #Teslimat noktası ataması burada yapılacak.
            taskHistory.save()

            robot.isBusy = True
            robot.save()

            p3 = RobotTaskHistory(Robot=robot, TaskHistory=taskHistory, RobotStatus=1)
            p3.save()

            t1 = RobotTaskHistoryLog(RobotTaskHistory=p3, RobotStatus=1, LogTime=datetime.datetime.now())
            t1.save()

            returnlist.append(ret)




           #Görevlere en yakın dok arabasını ata ve görev noktası olarak dokun konumuna güncelle. Görevin sürecini boş dok arabası iletiliyor olarak ata.
       #Görevleri listele
       #Görevi olmayan robotları getir.
       #Eğer görevi olmayan robot sayısı görev sayısından azsa kalan kısmı çalışmakta olan robotlar arasında görevi en kısa sürede bitecek olandan seç. Robotların üzerindeki görevin bitiş noktasını robotun konumu olarak al.
       #Tüm görevlerin tüm robotlara olan uzaklıklarını hesapla. Optimum toplam yol için FODPSO algoritmasını çalıştır.
       #Optimizasyon sonucuna göre robotları göreve ata ve harekete başla.
    #eğer atanmamış görev sayısı birden fazla değilse en kısa mesafedeki robotu ata ve harekete başla.

    #if path != False:
            #        if algo == "astar":
            #   path.append(start)
            #model = {}
            #model["robot"] = tasks[rob]["robot"].Name
            #model["goal"] = goals[g].Code
            #model["path"] = path
    #models.append(model)

    #return JsonResponse(models, safe=False)

    return JsonResponse(returnlist, safe=False)



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
                             StartStation=startStationTask, TaskStatus=taskStatus, isActive=True, isExitTask = False, Map=map)
            p1.save()

            if workSatation != None:
                #Dok arabalarını makinenin çıkış noktasına götürmek için yeni bir iş oluşturuyoruz. TaskStatusu=2 yaparak en uygun dok arabasını atamasını sağlıyoruz.
                p2 = TaskHistory(TransferredObject=entity, WorkStation=workSatation, WorkOrder=taskHistory["WorkOrder"],
                                 StartStation=startStationTask, TaskStatus=1, isActive=True, isExitTask = True, Map=map)
                p2.save()

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

