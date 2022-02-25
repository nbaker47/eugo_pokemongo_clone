from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from eugo.models import Lecturer
from eugo.forms import *


def index(request):
    return render(request, 'index.html')

def battle(request):
    return render(request, 'battle.html')

def map(request):
    lec = Lecturer.objects.all()
    return render(request, 'map.html',{'lec': lec})

def login(request):
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        #print(request.POST)

        firstname   =   request.POST['firstname']
        surname     =   request.POST['surname']
        username    =   request.POST['username']
        password1   =   request.POST['password1']
        password2   =   request.POST['password2']

        print(firstname, " - ", surname, " - ", username, " - ", password1, " - ", password2)

        #Do salt etc here i think. checking username hasnt been taken
        #We could do validation here but I think doing it in JavaScript might be easier

    return render(request, 'register.html')

def player(request):
    return render(request, 'player.html')

def lecturers(request):
    return render(request, 'lecturers.html')

def lecturerdex(request):
    lec = Lecturer.objects.all()
    return render(request, 'lecturerdex.html',{'lec': lec})

def mapmod(request):
    if request.method == 'POST':
        print(request.POST)
        '''
        form = lecMakerForm(request.POST)
        if form.is_valid():
            print("Successfully made new Lecturer event")
            print(form)
        else:
            form = lecMakerForm()
            print("ERROR! failed to make new lecturer event!")
            print(form)
        '''
        duration = request.POST['duration']
        name = request.POST['name']
        hp = request.POST['hp']
        attack = request.POST['attack']
        type = request.POST['type']
        sprite = "teacher_" + str(request.POST['sprite']) + ".png"
        coords = request.POST['coords']
        gameop = request.POST['gameop']
        newLec = Lecturer(duration=duration, name=name, hp=hp, attack=attack, sprite=sprite, pos=coords, type=type, wildOrBattle=gameop)
        newLec.save()
        print(newLec)

    lec = Lecturer.objects.all()
    return render(request, 'mapmod.html',{'lec': lec})
