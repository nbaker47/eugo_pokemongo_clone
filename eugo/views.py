from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from eugo.models import Lecturer
from eugo.forms import *
from random import randint
import requests
import qrtools
import re
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError

def index(request):
    return render(request, 'index.html')

def battle(request):
    return render(request, 'battle.html')

def signin(request): #cannot be named login because of imported function

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
   
        print(username, password)
        user = authenticate(request, username=username, password=password)

        print(user)
        if user is not None:
            login(request, user)
            firstname = user.first_name

            return render(request, "index.html", {'firstname': firstname})

    return render(request, 'login.html')

def signout(request):
    logout(request)
    messages.success(request, "Logged Out")
    return redirect('index')

def register(request):
    if request.method == "POST":
        #print(request.POST)

        firstname   =   request.POST['firstname']
        surname     =   request.POST['surname']
        email       =   request.POST['email']
        username    =   request.POST['username']
        password    =   request.POST['password1']
        
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = surname
            user.save()
            print(user)
        except IntegrityError:
            messages.error(request, "Username already created")
            return redirect('/eugo/register')


        #Need to check emails to make sure it isnt already used
        #We could do validation here but I think doing it in JavaScript might be easier

    return render(request, 'register.html')

def player(request):
    return render(request, 'player.html')

def lecturers(request):
    return render(request, 'lecturers.html')

def lecturerdex(request):
    lec = Lecturer.objects.all()
    return render(request, 'lecturerdex.html',{'lec': lec})

def catch(request):
    if request.method == 'POST':
        #lec_id = request.POST['lecID']
        lec_id = str(request.POST.get('lecID'))
        print("lec ID: " + lec_id)

    lec = Lecturer.objects.filter(id = lec_id)
    return render(request, 'catch.html',{'lec': lec})

def newcatch(request):
    if request.method == 'POST':
        lec_id = str(request.POST.get('lec_id'))

        #test output
        print("lec ID: " + lec_id + " was caught")

    lec = Lecturer.objects.filter(id = lec_id)
    return render(request, 'catch.html',{'lec': lec})

def map(request):
    if request.method == 'POST':
        qrUrl = request.POST['qrUrl']
        try:
            qr = qrtools.QR()
            qr.decode(qrUrl)
            print (qr.data)
        except:
            print('error reading QR')

    lec = Lecturer.objects.all()
    return render(request, 'map.html',{'lec': lec})



def mapmod(request):
    if request.method == 'POST':
        print(request.POST)
        #retrive POST var
        duration = request.POST['duration']
        name = request.POST['name']
        name = re.sub(r'[^\w\s]', '', name)#sanitise
        hp = request.POST['hp']
        attack = request.POST['attack']
        type = request.POST['type']
        sprite = "teacher_" + str(request.POST['sprite']) + ".png"
        coords = request.POST['coords']
        gameop = request.POST['gameop']
        #generate QR
        qr_key = str(randint(10000,20000)) + name
        qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + qr_key
        #save qr to file
        img_data = requests.get(qrUrl).content
        file_path = 'eugo/static/eugo/img/qr/' + qr_key + '.png' 
        with open(file_path, 'wb') as handler:
            handler.write(img_data)
        #create new row in Lecturer table
        newLec = Lecturer(id=qr_key, duration=duration, name=name, hp=hp, attack=attack, sprite=sprite, pos=coords, type=type, wildOrBattle=gameop, qrUrl = qr_key+'.png')
        newLec.save()
        print(newLec)

    lec = Lecturer.objects.all()
    return render(request, 'mapmod.html',{'lec': lec})
