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



class TransferVehicle(models.Model):
    Barcode = models.CharField(max_length=250)
    isActive = models.BooleanField(default=False)
    isFull = models.BooleanField(default=False)
    LastPosX = models.IntegerField(null=True)
    LastPosY = models.IntegerField(null=True)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Barcode


class StartStation(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    isFull = models.BooleanField(default=False)
    Position = models.CharField(max_length=2000, blank=True)
    CenterX = models.IntegerField(default=0)
    CenterY = models.IntegerField(default=0)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code


class FinishStation(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    isFull = models.BooleanField(default=False)
    Position = models.CharField(max_length=2000, blank=True)
    CenterX = models.IntegerField(default=0)
    CenterY = models.IntegerField(default=0)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code



class TransferredObjects(models.Model):
    Barcode = models.CharField(max_length=250)
    isActive = models.BooleanField(default=False)
    LastPosX = models.IntegerField(null=True)
    LastPosY = models.IntegerField(null=True)
    Length = models.IntegerField(null=True)
    StartStation = models.ForeignKey(StartStation, on_delete=models.DO_NOTHING, related_name='StartStation_TO', blank=True, null=True)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)
    TransferVehicle = models.ForeignKey(TransferVehicle, on_delete=models.DO_NOTHING, related_name='TransferVehicle_TO', blank=True, null=True)
    def __str__(self):
        return self.Barcode


class WorkStation(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    Position = models.CharField(max_length=2000, blank=True)
    EnterPosX = models.IntegerField()
    EnterPosY = models.IntegerField()
    ExitPosX = models.IntegerField()
    ExitPosY = models.IntegerField()
    SecondPerMeter = models.IntegerField(null=True)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code





class WaitingStation(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    isFull = models.BooleanField(default=False)
    Position = models.CharField(max_length=2000, blank=True)
    CenterX = models.IntegerField(default=0)
    CenterY = models.IntegerField(default=0)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code



class TaskHistory(models.Model):
    TransferredObject = models.ForeignKey(TransferredObjects, on_delete=models.CASCADE, blank=False, null=False)
    TransferVehicle = models.ForeignKey(TransferVehicle, on_delete=models.DO_NOTHING, related_name='TransferVehicle_TOTask', blank=True, null=True)
    WorkStation = models.ForeignKey(WorkStation, on_delete=models.DO_NOTHING, related_name='WorkStation_TOTask', blank=True, null=True)
    WaitingStation = models.ForeignKey(WaitingStation, on_delete=models.DO_NOTHING, related_name='WaitingStation_TOTask', blank=True, null=True)
    FinishStation = models.ForeignKey(FinishStation, on_delete=models.DO_NOTHING, related_name='FinishStation_TOTask', blank=True, null=True)
    Robot = models.ForeignKey(Robot, on_delete=models.DO_NOTHING, related_name='Robot_TOTask', blank=True, null=True)
    WorkOrder = models.IntegerField(null=True)
    isCompleted = models.BooleanField(default=False)
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return self.TransferredObject.Barcode + " - " + str(self.WorkOrder)




class TObjectWaiting(models.Model):
    StartDateTime = models.DateTimeField()
    EnfDateTime = models.DateTimeField()
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)
    TransferredObjects = models.ForeignKey(TransferredObjects, on_delete=models.DO_NOTHING, blank=True, null=True)
    WaitingStation = models.ForeignKey(WaitingStation, on_delete=models.DO_NOTHING, blank=True, null=True)



class ChargingStation(models.Model):
    Code = models.CharField(max_length=250)
    Name = models.CharField(max_length=500)
    isActive = models.BooleanField(default=False)
    isFull = models.BooleanField(default=False)
    Position = models.CharField(max_length=2000, blank=True)
    CenterX = models.IntegerField(default=0)
    CenterY = models.IntegerField(default=0)
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.Code



class RobotCharging(models.Model):
    StartDateTime = models.DateTimeField()
    EnfDateTime = models.DateTimeField()
    Map = models.ForeignKey(Map, on_delete=models.DO_NOTHING, blank=True, null=True)
    Robot = models.ForeignKey(Robot, on_delete=models.DO_NOTHING, blank=True, null=True)
    ChargingStation = models.ForeignKey(ChargingStation, on_delete=models.DO_NOTHING, blank=True, null=True)


