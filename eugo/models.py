from django.db import models

# Create your models here.
class Lecturer(models.Model):
    name = models.CharField(max_length=255)
    duration = models.SlugField(unique=True, max_length=255)
    hp = models.TextField()
    attack = models.DateTimeField(auto_now_add=True)
    subject = models.TextField()
    sprite = models.TextField()
    pos = models.TextField()
    lecID = models.TextField()