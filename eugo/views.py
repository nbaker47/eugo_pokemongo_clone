from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from eugo.models import Lecturer, Player, Hand
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

""" This is the method that handles the login page (cannot be named login because of built in function) """
def signin(request):
    # check if the method is post 
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        #try:
        print(username, password)
        user = authenticate(request, username=username, password=password)

        print(user)
        if user is not None:
            login(request, user)
            firstname = user.first_name

            return render(request, "index.html", {'firstname': firstname})
        #except no such table: auth_user

    return render(request, 'login.html')

def signout(request):
    logout(request)
    messages.success(request, "Logged Out")
    return redirect('index')

def register(request):
    if request.method == "POST":
        print(request.POST)

        firstname   =   request.POST['firstname']
        surname     =   request.POST['surname']
        email       =   request.POST['email']
        username    =   request.POST['username']
        password    =   request.POST['password1']
        sprite_no =  request.POST['sprite']
        sprite_url = "eugo/static/eugo/img/teacher_sprites/teacher_" + sprite_no + ".png"
        print("SPRITE URL::   " + sprite_url)

        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = surname
            user.save()
            p = Player(firstname = firstname, surname = surname, email = email, username = username, pokemon_caught = 0, sprite_url = sprite_url)
            p.save()
            print(p)
            print(user)
            return redirect('/eugo/login')
         
        except IntegrityError as e:
            messages.error(sprite_url)
            messages.error(request, e)
            return redirect('/eugo/register')
        # comment


        #Need to check emails to make sure it isnt already used
        #We could do validation here but I think doing it in JavaScript might be easier

    return render(request, 'register.html')

def player(request):
    # check if they are submitting a POST method or just visiting
    if request.method == "POST":
        # make sure that the usplayerer is authenticated (not anonymous user)
        if request.user.is_authenticated:
            # username is request.user.username
            password = request.POST['pass1']
            user = User.objects.get(username__exact=request.user.username)
            # change the password
            user.set_password(password)
            # save the user object
            user.save()
            # redirect to login ()
            return redirect("/eugo/login")
    # check if the user is authenticated
    if request.user.is_authenticated:
        cur_play = Player.objects.get(email=request.user.email)
        player_img = str(cur_play.sprite_url)[4:]
        name = cur_play.username
        return render(request, "player.html", {"player":player_img})
    else:
        # if they arent redirect to login
        return redirect("/eugo/login")
    

def lecturers(request):
    un = request.user.username
    player = Player.objects.filter(username=un)[0]
    hands = Hand.objects.filter(username = player)

    return render(request, 'lecturers.html',{'hand': hands})

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
        #gets lecturer that was cught by id
        lecid = str(request.POST.get('lec_id'))
        lec = Lecturer.objects.filter(id = lecid)

        #gets the current user
        current_user = request.user
        un = current_user.username
        player = Player.objects.filter(username=un)[0]

        #addds the lec to the players hand
        player.pokemon_caught = player.pokemon_caught+1
        player.save()

        h = Hand(username = player, lec_id = lec[0])
        h.save()

        print(lec[0].name + " was caputred by " + un )

    return render(request, 'catch.html', {'lec': lec})

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
    players = Player.objects.all()
    player_vals = players.values()
    leaderboard = sorted(player_vals, key=lambda d: d['pokemon_caught'], reverse=True)
    #print(leaderboard)
    return render(request, 'map.html',{'lec': lec, 'players': leaderboard})

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
