from django.db import models

# Create your models here.



class Tenant(models.Model):
    Name = models.CharField(max_length=500)

    def __str__(self):
        return self.Name


class SubNet(models.Model):
    Name = models.CharField(max_length=500)
    Tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    def __str__(self):
        return self.Name


class RobotModel(models.Model):
    Name = models.CharField(max_length=250)
    Producer = models.CharField(max_length=250)
    Image = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.Name + ' - ' + self.Producer


class Map(models.Model):
    Name = models.CharField(max_length=250)
    SubNet = models.ForeignKey(SubNet, on_delete=models.CASCADE)
    Width = models.IntegerField(null=True)
    Height = models.IntegerField(null=True)
    Distance = models.IntegerField(null=True)
    def __str__(self):
        return self.Name


class Robot(models.Model):
    Name = models.CharField(max_length=250)
    Code = models.CharField(max_length=50)
    RobotModel = models.ForeignKey(RobotModel, on_delete=models.CASCADE)
    isActive = models.BooleanField(default=False)
    LastCoordX = models.IntegerField(null=True)
    LastCoordY = models.IntegerField(null=True)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)
    def __str__(self):
        return self.Name + ' - ' + self.Code


class RobotActivity(models.Model):
    Time = models.DateField()
    Robot = models.ForeignKey(Robot, on_delete=models.CASCADE)

class ObstaclePoint(models.Model):
    Left = models.IntegerField()
    Right = models.IntegerField()
    Top = models.IntegerField()
    Bottom = models.IntegerField()
    CenterX = models.IntegerField()
    CenterY = models.IntegerField()
    Position = models.CharField(blank=True, max_length=2000),
    Position2 = models.CharField(blank=True, max_length=2000),
    Map = models.ForeignKey(Map, on_delete=models.CASCADE)
    def __str__(self):
        return "Map: " + self.Map.Name + "   /   Location: " + str(self.Left) + " - " + str(self.Right) + " - " + str(self.Top) + " - " + str(self.Bottom)

class MapGoalPoint(models.Model):
    Code = models.CharField(max_length=50)
    Left = models.IntegerField()
    Right = models.IntegerField()
    Top = models.IntegerField()
    Bottom = models.IntegerField()
    Map = models.ForeignKey(Map, on_delete=models.CASCADE)
    def __str__(self):
        return "Map: " + self.Map.Name + "   /   Code: " + str(self.Code) + "   /   Location: " + str(self.Left) + " - " + str(self.Right) + " - " + str(self.Top) + " - " + str(self.Bottom)

class Sticker(models.Model):
    Code = models.CharField(max_length=250)
    UniqueCode = models.CharField(max_length=500)
    Map = models.ForeignKey(Map, on_delete=models.CASCADE)

    def __str__(self):
        return self.Code


class Mapping(models.Model):
    CurrentSticker = models.ForeignKey(Sticker, on_delete=models.DO_NOTHING, related_name='custom_sticker')
    Left = models.ForeignKey(Sticker, on_delete=models.DO_NOTHING, related_name='left_sticker', blank=True, null=True)
    Right = models.ForeignKey(Sticker, on_delete=models.DO_NOTHING, related_name='right_sticker', blank=True, null=True)
    Top = models.ForeignKey(Sticker, on_delete=models.DO_NOTHING, related_name='top_sticker', blank=True, null=True)
    Down = models.ForeignKey(Sticker, on_delete=models.DO_NOTHING, related_name='down_sticker', blank=True, null=True)
    Map = models.ForeignKey(Map, on_delete=models.CASCADE)
    def __str__(self):
        return self.CurrentSticker.Code


class RobotLocation(models.Model):
    RobotActivity = models.ForeignKey(RobotActivity, on_delete=models.CASCADE)
    Sticker = models.ForeignKey(Sticker, on_delete=models.DO_NOTHING)
    PositionX = models.FloatField()
    PositionY = models.FloatField()


class TransferredObjects(models.Model):
    Borcode = models.CharField(max_length=250)
    isActive = models.BooleanField(default=False)
    LastPosX = models.IntegerField(null=True)
    LastPosY = models.IntegerField(null=True)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Borcode


class TransferredObjectsTask(models.Model):
    Code = models.CharField(max_length=250)
    TransferredObjects = models.ForeignKey(TransferredObjects, on_delete=models.CASCADE)
    isCompleted = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return self.Code


class WorkStation(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    Position = models.CharField(max_length=2000, blank=True)
    EnterPosX = models.FloatField()
    EnterPosY = models.FloatField()
    ExitPosX = models.FloatField()
    ExitPosY = models.FloatField()
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code


class TaskHistory(models.Model):
    TransferredObjectsTask = models.ForeignKey(TransferredObjectsTask, on_delete=models.CASCADE, blank=False, null=False)
    WorkStation = models.ForeignKey(WorkStation, on_delete=models.DO_NOTHING, related_name='WorkStation_TOTask', blank=True, null=True)
    Robot = models.ForeignKey(Robot, on_delete=models.DO_NOTHING, related_name='Robot_TOTask', blank=True, null=True)
    WorkOrder = models.IntegerField(null=True)
    isCompleted = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return self.TransferredObjectsTask.Code + " - " + str(self.WorkOrder)


class WaitingStation(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code

class WaitingStationSection(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    isFull = models.BooleanField(default=False)
    WaitingStation = models.ForeignKey(WaitingStation, on_delete=models.CASCADE)
    TransferredObjects = models.ForeignKey(TransferredObjects, on_delete=models.DO_NOTHING, blank=True,null=True)
    Position = models.CharField(max_length=2000, blank=True)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code

class ChargingStation(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code


class ChargingStationSection(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    isFull = models.BooleanField(default=False)
    ChargingStation = models.ForeignKey(ChargingStation, on_delete=models.CASCADE)
    Robot = models.ForeignKey(Robot, on_delete=models.DO_NOTHING, blank=True,null=True)
    Position = models.CharField(max_length=2000, blank=True)

    def __str__(self):
        return self.Code
