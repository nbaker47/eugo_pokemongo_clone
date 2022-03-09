from django.contrib import admin
from .models import *
from django.apps import apps

models = apps.get_models()

# register the models
for model in models:
    try:
        admin.site.register(model)
    except:
        pass