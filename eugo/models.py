from django.db import models


class Player(models.Model):
   username = models.CharField(max_length=20)
   password = models.CharField(max_length=255)
   is_admin = models.BooleanField(default=False)

# Create your models here.
class Lecturer(models.Model):
    duration = models.IntegerField()
    name = models.CharField(max_length=100)
    hp = models.IntegerField()
    attack = models.IntegerField()
    sprite = models.CharField(max_length=100)
    pos = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    wildOrBattle = models.CharField(max_length=100)

    def __str__(self):
        return (self.name)