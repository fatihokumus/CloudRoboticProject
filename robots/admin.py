from django.contrib import admin
from .models import Robot, RobotModel, Tenant, SubNet, Map, Sticker, Mapping,  TransferredObjects, TransferredObjectsTask, WorkStation, WaitingStation, ChargingStation

admin.site.register([Robot, RobotModel, Tenant, SubNet, Map, Sticker, Mapping,  TransferredObjects, TransferredObjectsTask, WorkStation, WaitingStation, ChargingStation])

