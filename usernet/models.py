from django.db import models

class Tags(models.Model):
    tag = models.CharField(max_length=256)

    def __unicode__(self):
        return  self.tag

class People(models.Model):
    Usr_Name = models.CharField(max_length=256)
    Usr_Mobile = models.CharField(max_length=16, null=True)
    Usr_Remark = models.TextField(null= True)
    tags = models.ManyToManyField(Tags,null=True)
    active = models.IntegerField(null=True)
    isdel = models.IntegerField(null=True)
    uuid = models.CharField(max_length=256)

    Cluster_id = models.CharField(max_length=256)

    Prev_Usr = models.ForeignKey('self',related_name="Prev_related",null=True)
    Weight = models.IntegerField(null=True)
    Last_Update = models.DateTimeField(auto_now=True)


    def __unicode__(self):
        return self.Usr_Name


class ActiveUsr(models.Model):
    Usr_Name = models.CharField(max_length=256,null=True)
    OpenId = models.CharField(max_length=256,null=True)
    Level = models.IntegerField(null=True)
    Cluster_id = models.CharField(max_length=256)
    is_manager = models.IntegerField(null=True)
    uuid = models.CharField(max_length=256)

