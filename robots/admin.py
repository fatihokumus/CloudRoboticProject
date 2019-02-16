from django.contrib import admin
from .models import Robot, RobotModel, Tenant, SubNet, Map, Sticker, Mapping, MapObstaclePoint, MapGoalPoint

admin.site.register([Robot, RobotModel, Tenant, SubNet, Map, Sticker, Mapping, MapObstaclePoint, MapGoalPoint])

