from django.contrib import admin
from .models import Robot, RobotModel, Tenant, SubNet, Map, Tag, TransferredObject, WorkStation, WaitingStation, ChargingStation, TransferVehicle, TaskHistory

admin.site.register([Robot, RobotModel, Tenant, SubNet, Map, Tag, TransferredObject, WorkStation, WaitingStation, ChargingStation, TransferVehicle, TaskHistory])

