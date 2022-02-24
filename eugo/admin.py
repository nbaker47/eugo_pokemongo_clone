from django.contrib import admin
from .models import Player, Lecturer

# register thr models
admin.site.register(Player)
admin.site.register(Lecturer)