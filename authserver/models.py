from django.db import models

class Device(models.Model):
    Gw_Id=models.CharField(max_length=100,null=True)
    Gw_Address=models.CharField(max_length=100,null=True)
    Gw_Port=models.CharField(max_length=100,null=True)

class People(models.Model):
    OpenId = models.CharField(max_length=256,null=True)
    Token = models.CharField(max_length=256,null=True)
    IsLogin = models.IntegerField(null=True)
    Mac = models.CharField(max_length=48,null=True)
    Gw_Id=models.CharField(max_length=100,null=True)

class APDevice(models.Model):
    device=models.ForeignKey(Device)
    Sys_Uptime = models.CharField(max_length=20)
    Sys_Memfree = models.CharField(max_length=20)
    Sys_Load = models.CharField(max_length=20)
    Wifidog_Uptime = models.CharField(max_length=20)
    S_Time = models.DateTimeField(auto_now_add=True)

class LoginTmp(models.Model):
    Token = models.CharField(max_length=256,null=True)
    Gw_Id=models.CharField(max_length=100,null=True)
    Gw_Address=models.CharField(max_length=100,null=True)
    Gw_Port=models.CharField(max_length=100,null=True)
    IsLogin = models.IntegerField(null=True)

class LoginHistory(models.Model):
    people = models.ForeignKey(People)
    Gw_Id=models.CharField(max_length=100,null=True)
    Login_Time=models.DateTimeField(auto_now_add=True)


