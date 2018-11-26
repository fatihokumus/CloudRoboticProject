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


class Robot(models.Model):
    Name = models.CharField(max_length=250)
    Code = models.CharField(max_length=50)
    RobotModel = models.ForeignKey(RobotModel, on_delete=models.CASCADE)
    Tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    SubNet = models.ForeignKey(SubNet, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.Name + ' - ' + self.Code


class RobotActivity(models.Model):
    Time = models.DateField()
    Robot = models.ForeignKey(Robot, on_delete=models.CASCADE)


class Map(models.Model):
    Name = models.CharField(max_length=250)
    SubNet = models.ForeignKey(SubNet, on_delete=models.CASCADE)

    def __str__(self):
        return self.Name



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



