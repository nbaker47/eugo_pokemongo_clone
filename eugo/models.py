from django.db import models

# Create your models here.
class Lecturer(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    duration = models.IntegerField()
    name = models.CharField(max_length=100)
    hp = models.IntegerField()
    attack = models.IntegerField()
    sprite = models.CharField(max_length=100)
    pos = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    wildOrBattle = models.CharField(max_length=100)
    qrUrl = models.CharField(max_length=500)

    def __str__(self):
        return (self.name)