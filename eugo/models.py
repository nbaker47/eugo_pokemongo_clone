from django.db import models


class Player(models.Model):
   firstname    =   models.CharField(max_length=30, null=True)
   surname      =   models.CharField(max_length=30, null=True)
   username     =   models.CharField(max_length=20)
   password     =   models.CharField(max_length=255)
   salt         =   models.CharField(max_length=10, null=True)
   is_admin     =   models.BooleanField(default=False)

   def __str__(self):
       return(self.username)

# Create your models here.
class Lecturer(models.Model):
    duration = models.IntegerField()
    name = models.CharField(max_length=100)
    hp = models.IntegerField()
    attack = models.IntegerField()
    sprite = models.CharField(max_length=100)
    pos = models.CharField(max_length=100)
    lecturer_type = models.CharField(max_length=100)
    is_wild = models.BooleanField(default=True)

    def __str__(self):
        return (self.name)