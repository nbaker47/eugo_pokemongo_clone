""" ---------------------------- IMPORTS -------------------------------------------------------------- """
""" IMPORTS FROM EUGO -------- """
from eugo.models import *                                       # import the models (database)
from eugo.forms import *                                        # all of the forms ????????? TODO
from eugo.models import Player
import os.path

""" IMPORTS FROM DJANGO ------ """
from django.shortcuts import redirect, render                   # to render templates and redirect 
from django.http import HttpResponse                            # send a http response using django
from django.template import loader# """ TODO: DEAD IMPORT? """
from django.shortcuts import get_object_or_404 #""" TODO: DEAD IMPORT? """
from django.contrib.auth.models import User                     # to be able to access the user database
from django.contrib.auth import authenticate, login, logout     # built in django methods that handle the
                                                                # user moving through pages
from django.contrib import messages                             # handle sending messages to the client 
from django.db import IntegrityError                          # throw integrity errors (database)
from django.utils import timezone as tz

""" OTHER IMPORTS ------------ """
import requests                                                 # for the image data
import qrtools                                                  # for scanning and recognising the qr code
import re                                                       # for regex patterns
from random import randint                                      # random is self-explanatory
from datetime import datetime
import copy
import datetime
import urllib.request
import random

""" ---------------------------- VIEWS ---------------------------------------------------------------- """
""" INDEX -------------------- """
""" This method to handle index.html (not much going on because this is just teh cover page) """
def index(request):
    return render(request, 'index.html')


""" BATTLE ------------------- """
""" This method to handle the battle.html """
def battle(request):
    #lec_id = request.POST['lecID']
    # get the lec and event IDs
    lec_id = str(request.POST.get('lecID'))
    event_id = request.POST.get('eventID')

    # get the lecturer object from its id
    lec = Lecturer.objects.filter(id = lec_id)
    # return the render with the lecturer and event IDs
    un = request.user.username
    # get the player object that matches the username
    player = Player.objects.filter(username=un)[0]
    items = [player.balls, player.extensions]

    hands = Hand.objects.filter(username = player)

    print(event_id)

    return render(request, 'battle.html',{'lec': lec, 'eve': event_id, 'is_admin': get_admin(request), 'items': items, "playerLecs" : hands})

""" STARTBATTLE -------------- """
""" This function handles making the battles and then playing them out """
def startbattle(request):
    print(request.POST)

    player_lec_id = request.POST.get('playerLecturerID')
    event_id = request.POST.get('eventID')
    opp_lec = MapEvent.objects.get(id = event_id).lec_id
    player_lec = Lecturer.objects.get(id = player_lec_id)
    un = request.user.username
    player = Player.objects.filter(username=un)[0]

    #create move list (player always first)
    move_list = list()
    p_hp = player_lec.hp
    o_hp = opp_lec.hp
    if(request.POST.get("extension")):
        o_hp = int(o_hp*0.8)
        opp_lec.hp = int(opp_lec.hp*0.8)
        player.extensions -= 1
        player.save()

    result = ""

    print(o_hp)
    while True:
        next_attack = int( random.random() * player_lec.attack )
        move_list.append(next_attack)
        o_hp -= next_attack
        
        if(o_hp <= 0):
            
            result = "you won!"
            break
        next_attack = int( random.random() * opp_lec.attack )
        move_list.append(next_attack)
        p_hp -= next_attack
        if(p_hp <= 0):
            result = opp_lec.name + " won"
            break

    items = [player.balls, player.extensions]

    ce = CompleteEvents(username = player, event = MapEvent.objects.get(id = event_id))
    ce.save()

    return render(request, 'battlegame.html',{'player_lec': player_lec, 'lec' : opp_lec,'eve': event_id, 'is_admin': get_admin(request), 'items': items, 'moves': move_list, "result": result})
        

    

""" SIGNIN ------------------- """
""" This is the method that handles the login page (cannot be named login because of built in function) """
def signin(request):
    # check if the method is POST (if they are sending in form data) 
    if request.method == "POST":
        # if so get the username and password from the request
        username = request.POST['username']
        password = request.POST['password']

        # print the username and password to the console (for debugging)
        print(username, password)
        # try and authenticate the user
        user = authenticate(request, username=username, password=password)

        # check if the user has been authenticated
        print(user)
        if user is not None:
            # log the user into the request
            login(request, user)
            firstname = user.first_name
            # send the first name with the template 
            return render(request, "index.html", {'firstname': firstname})
        #except no such table: auth_user
    
    # if methd is not POST then just render the normal template
    return render(request, 'login.html')


""" SIGNOUT ------------------ """
""" This method signs the user out and redirects them """
def signout(request):
    # logout the user (using django)
    logout(request)
    # notify the user they have been signed out
    messages.success(request, "Logged Out")
    # redirect the user to index
    return redirect('index')


""" A custom class to throw an "EmailExists" exception for register if the email is linked to another account """
class EmailExistsException(Exception):
    pass

""" REGISTER ----------------- """
""" This method which handles register.html and the registering of new users """
def register(request):
    # check if the method is POST (data is sent to register the user)
    if request.method == "POST":
        print(request.POST)

        # get all of the data from the request
        firstname   =   request.POST['firstname']
        surname     =   request.POST['surname']
        email       =   request.POST['email']
        username    =   request.POST['username']
        password    =   request.POST['password1']
        staffno     =   request.POST['staffno']

        #Custom sprite or preset?:
        try:
            custom_s_url = request.POST['canvas-output']
            if len(custom_s_url)> 1:
                #retrieve image from posted url
                sprite_url  =   "eugo/static/eugo/img/player_sprites/" + str(randint(100,999)) + ".png" #change to unique number later
                urllib.request.urlretrieve(custom_s_url, sprite_url)
                print("SPRITE URL::   " + sprite_url)
            else:
                try:
                    sprite_no   =   request.POST['sprite']
                    sprite_url  =   "eugo/static/eugo/img/teacher_sprites/teacher_" + sprite_no + ".png"
                    print(sprite_no)
                    print("SPRITE URL::   " + sprite_url)
                except Exception as e: print(e)
        except Exception as e: print(e)

        # try to make the new user in the database
        try:
            # Stops multiple accounts being registered with the same email

            if Player.objects.filter(email=email).exists():
                print(f"[{username}] email ({email}) already exists")
                raise EmailExistsException("Email is already registered")

            # create the new user object in the database and assign attributes
            print(f"[{username}] attempting account creation")
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = surname

            # check if staff code is correct (If so set as staff)
            if staffno == "123456":
                print(f"[{username}] SET AS SUPERUSER/STAFF")
                is_admin = True
            
            else:
                print(f"[{username}] NOT A SUPERUSER/STAFF")
                is_admin = False
            

            # save the user in the User database
            user.save()
            print(f"[{username}] created user object")

            # create a new player in the Player database
            p = Player.objects.create(firstname = firstname, surname = surname, email = email, username = username, pokemon_caught = 0, sprite_url = sprite_url, is_admin = is_admin)
            # save the player in the Player database
            #p.save()
            print(f"[{username}] created player object")
            # Create the users friendlist
            FriendsList.objects.create(user1=p)
            
            #make friends list
            #fl = FriendsList(user1 = p)
            #fl.save()
            #try to fix bug where user is added to same friends list
            #try:
                #fl.remove_frend(p)
            #except:
             #   pass
            print(f"[{username}] created friends list")    

            #print("saved :", fl)

            # redirect to login screen (register successful)
            return redirect('/eugo/login/')

        except EmailExistsException:
            print(f"[{username}] used an already existing email")
            return redirect('/eugo/register/')

        # catch integrity errors (problem with database -> not registered)
        except IntegrityError as e:
            # semd appropriate messages to notify the user of the errors
            #messages.error(sprite_url)
            #messages.error(request, e)
            print(f"[{username}] raised IntegrityError")
            print(e)
            # redirect (so they can try again)
            return redirect('/eugo/register/')

        #Need to check emails to make sure it isnt already used
        #We could do validation here but I think doing it in JavaScript might be easier

    # if no form needs to be processed, then just sent the html file
    return render(request, 'register.html')


""" PLAYER ------------------- """
""" This method deals with handling player.html and the password change form in it """
def player(request):
    # check if the user is authenticated
    if request.user.is_authenticated:
        # check if they are submitting a POST method or just visiting
        if request.method == "POST":
            # make sure that the usplayerer is authenticated (not anonymous user)
            # username is request.user.username
            password = request.POST['pass1']
            user = User.objects.get(username__exact=request.user.username)
            # change the password
            user.set_password(password)
            # save the user object
            user.save()
            # redirect to login ()
            return redirect("/eugo/login")

        else:
            # check if the user is authenticated
            cur_play = Player.objects.get(email=request.user.email)
            # load the current sprite
            player_img = str(cur_play.sprite_url)[4:]
            # load the username
            name = cur_play.username
            # send the request with the sprite back to the player
            items = [cur_play.balls, cur_play.extensions]

            return render(request, "player.html", {"player":player_img, 'is_admin': get_admin(request), 'items': items})

    # if they arent redirect to login
    return redirect("/eugo/login")


""" LECTURERS ---------------- """
""" This method handles the lecturers link """
def lecturers(request):
    # get the username of the player
    un = request.user.username
    # get the player object that matches the username
    player = Player.objects.filter(username=un)[0]
    # get the hand of the player object
    hands = Hand.objects.filter(username = player)
    items = [player.balls, player.extensions]
    # finally, return the rendered template with the hand
    return render(request, 'lecturers.html',{'hand': hands, 'items': items, 'is_admin': get_admin(request)})


""" LECTURERDEX -------------- """
""" This method handles the lecturerdex link """
def lecturerdex(request):
    # get a list of all of the lecturers
    lec = Lecturer.objects.all()
    # return the render with the lecturers list
    # get the username of the player
    un = request.user.username
    # get the player object that matches the username
    player = Player.objects.filter(username=un)[0]
    items = [player.balls, player.extensions]
    return render(request, 'lecturerdex.html',{'lec': lec, 'is_admin': get_admin(request), 'items': items})


""" CATCH -------------------- """
""" This method handles the catch link and the catching of lecturers """
def catch(request):

    # check if the method is POST (a lecturer has been caught)
    if request.method == 'POST':
        #lec_id = request.POST['lecID']
        # get the lec and event IDs
        lec_id = str(request.POST.get('lecID'))
        event_id = request.POST.get('eventID')

        # print for debugging
        print("lec ID: " + lec_id)
        print("event ID: " + event_id)

    # get the lecturer object from its id
    lec = Lecturer.objects.filter(id = lec_id)
    # return the render with the lecturer and event IDs
    un = request.user.username
    # get the player object that matches the username
    player = Player.objects.filter(username=un)[0]
    items = [player.balls, player.extensions]
    return render(request, 'catch.html',{'lec': lec, 'eve': event_id, 'is_admin': get_admin(request), 'items': items})


""" NEWCATCH ----------------- """
""" This method also handles the catching of lecturers """
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
        player.balls = request.POST.get("balls")
        player.save()

        h = Hand(username = player, lec_id = lec[0])
        h.save()

        #adds the event to the list of events completed my the user 
        event_id = request.POST.get("event_id")
        mapEvent = MapEvent.objects.filter(id=event_id)[0]
        ce = CompleteEvents(username = player, event = mapEvent)
        ce.save()

        print(lec[0].name + " was caputred by " + un )
        

    return render(request, 'catch.html', {'lec': lec})


""" NOCATCH ----------------- """
""" This method is for when the user fails a catch """
def nocatch(request):
    if request.method == 'POST':

        #gets lecturer that want caught
        lecid = str(request.POST.get('lec_id'))
        lec = Lecturer.objects.filter(id = lecid)

        #gets the current user
        current_user = request.user
        un = current_user.username
        player = Player.objects.filter(username=un)[0]

        player.balls = 0
        player.save()
        #adds the event to the list of events completed my the user 
        event_id = request.POST.get("event_id")
        mapEvent = MapEvent.objects.filter(id=event_id)[0]
        ce = CompleteEvents(username = player, event = mapEvent)
        ce.save()
        print(ce)

        

    return render(request, 'catch.html', {'lec': lec})


""" MAP ---------------------- """
""" This method handles the map link and its forms """
def map(request):
    # check if the request method is POST (corresponding to QR scans)
    if request.method == 'POST':
        # if it is get the QR URL
        qrUrl = request.POST.get('qrUrl')
        # try decoding the QR
        try:
            qr = qrtools.QR()
            qr.decode(qrUrl)
            print (qr.data)
        except:
            print('error reading QR')

    #gets the current user
    current_user = request.user
    un = current_user.username
    player = Player.objects.filter(username=un)[0]

    # Sets if the user is a admin - gives it to the template
    is_admin = player.is_admin

    lec = Lecturer.objects.all()
    
    # load the player objects on the map
    players = Player.objects.filter(is_admin=False)
    player_vals = players.values()

    # fetch and sort the leaderboard
    leaderboard = sorted(player_vals, key=lambda d: d['pokemon_caught'], reverse=True)
   
    # get all of the chat messages
    all_messages = ChatMessage.objects.all()
    #print(leaderboard)
    mapEvent = copy.deepcopy(list(MapEvent.objects.all()))

    if(request.POST.get("stopID")):
        stop = LectStop.objects.get(id = request.POST.get("stopID"))
        player.balls = player.balls + stop.balls
        player.extensions = player.extensions + stop.extensions
        player.save()
        #add to complete stops
        print(player)
        print(stop)
        x = CompleteStops(username = player, stop = stop)
        x.save()

    #remove completed events from data sent to page
    completed_events = CompleteEvents.objects.all()
    for i in completed_events:
        try:
            if(i.username == player):
                mapEvent.remove(i.event)
        except:
            # removes completed events refrencing events that no longer exist
            i.delete()
        

    #remove outdated events from whole database  
    try:
        for i in mapEvent:
            if((tz.now() - i.created_at).total_seconds() > i.lec_id.duration*60):
                mapEvent.remove(i.event)
    except:
        i.delete()
        
    
    #get incoming friend requests:
    reciever = Player.objects.get(username = request.user.username)
    try:
        incoming_friend_req = []
        incoming_friend_req.append(FriendRequest.objects.get(reciever=reciever, is_active=True))
    except:
        pass

    #get all friends
    try:
        user = Player.objects.get(username = request.user.username)
        friends = FriendsList.objects.get(user1= user).friends.split(',')[1:]
        friend2 = []
        for f in friends:
            friend2.append(Player.objects.get(pk=f))
    except:
        friend2 = []

    stops = list(LectStop.objects.all())
    completeStops = CompleteStops.objects.all()
    for s in completeStops:
        try:
            if(s.username == player):
                stops.remove(s.stop)
        except:
            # removes completed events refrencing events that no longer exist
            print("test")
            s.delete()

    items = [player.balls, player.extensions]

    #print("FRIENDS :", friends)
    # return the html render, giving it all of the corresponding data
    return render(request, 'map.html',{'lec': lec, 'players': leaderboard, 'mapEvent': mapEvent, 'incomingReq': incoming_friend_req, 'friends': friend2, 'stops': stops, 'is_admin': is_admin, 'items': items})


""" FRIEND REQ --------------- """
""" This method handles the sending and accepting of friend requests """
def friendreq(request):
    # print(request.POST)
    # check if POST method is being used (if they are sending a request or just want the page)
    if request.method == 'POST':
        # retrieve sender/recipient post data:
        type            =   request.POST['type']
        sender_name     =   request.POST['sender']
        sender          =   Player.objects.get(username = sender_name)
        reciever_name   =   request.POST['reciever']
        reciever        =   Player.objects.get(username = reciever_name)

        # check if the user is sending or accepting a friend request
        if type == 'send':
          
            request_exists = FriendRequest.objects.filter(sender=sender, reciever=reciever).exists()

            if not request_exists:
              # if the friend request is sent, then create a new request in the database
              new_friend_req = FriendRequest(sender=sender, reciever=reciever)
              # save the request
              new_friend_req.save()
              # print for debug
              print(f"[{sender_name}] send friend request to '{reciever_name}'")
              # send the success message
              messages.success(request, "friend request sent")

        elif type == 'accept':
            # if a friend request is being accepted then just accept it 
            friend_req = FriendRequest.objects.get(sender=sender, reciever=reciever)
            friend_req.accept()
            # Delete the request
            friend_req.delete()
            print(f"[{sender_name}] accepted a friend request from '{reciever_name}'")

        elif type == 'unfriend':
            print(f"[{sender}] Started unfriend process with '{reciever}'")
            """ remove from sender friend list """
            # get sender friend list
            fl = FriendsList.objects.filter(user1=sender)[0]
            # remove from list
            fl.remove_friend(reciever)
            # save the list
            fl.save()

            """ remove from reciever friend list """
            # get the reciever friend list
            fl = FriendsList.objects.filter(user1=reciever)[0]
            # remove sender from list
            fl.remove_friend(sender)
            # save the list
            fl.save()

    # finally, return the map render
    return render(request, 'map.html')


""" MAPMOD ------------------- """
""" This method handles the mapmod link (admin map) and the ability to add more events """
def mapmod(request):
    
    current_user = request.user
    un = current_user.username
    player = Player.objects.filter(username=un)[0]
    
    # If the user isn't a admin then it sends them back to map
    # MAPMOD removes it from the html. But incase they try getting into MAPMOD through entering the url
    if player.is_admin == False: 
        print("\nNot admin sending back")
        return redirect('/eugo/map/')

    # check if the request method is POST (a new event is being added)
    if request.method == 'POST':
        # get the operation being performed from the admin
        gameop = request.POST.get('gameop')

        # if the event is lecNewLi then create the new lecturer (add to database + generate QR)
        if(gameop == 'lecNewLi'):
            print(request.POST)
            # get the lecturer attributes from the POST request
            duration = request.POST.get('duration')
            # retrive and sanitise the name
            name = request.POST.get('name')
            name = re.sub(r'[^\w\s]', '', name)
            hp = request.POST.get('hp')
            attack = request.POST.get('attack')
            type = request.POST.get('type')
            sprite = "teacher_" + str(request.POST.get('sprite')) + ".png"
            
            # generate the QR code for the lecturer
            qr_key = str(randint(10000,20000)) + name
            qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + qr_key + ".png"
            # save the QR to the file
            img_data = requests.get(qrUrl).content
            file_path = 'eugo/static/eugo/img/qr/' + qr_key + '.png' 
            #with open(file_path, 'wb') as handler:
               # handler.write(img_data)
            # create the new lecturer int eh Lecturer table
            newLec = Lecturer(id=qr_key, duration=duration, name=name, hp=hp, attack=attack, sprite=sprite, type=type, qrUrl = qrUrl)
            # save the new lecturer
            newLec.save()
            print(newLec)
        #new pokistop
        elif(gameop == 'newStopLi'):
            print(request.POST)


            balls = request.POST.get('balls')
            extensions = request.POST.get('extensions')
            coords = request.POST.get('coords')
            now = datetime.datetime.now() # current date and time
            id = str(balls) + now.strftime("%H:%M:%S").replace(":", "") + str(extensions)

            #generate qr code
            qr_key = str(randint(10000,20000)) + id
            qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + qr_key
            # save the QR to the file
            img_data = requests.get(qrUrl).content
            file_path = 'eugo/static/eugo/img/qr/' + qr_key + '.png' 
            with open(file_path, 'wb') as handler:
                handler.write(img_data)

            newStop = LectStop(id = id, balls = balls, extensions = extensions, qrUrl = qr_key+'.png', pos=coords)
            newStop.save()

        # create a new event
        else:
            # get the lecturerID, lecturer objects and co-ordinates of the lecturer from the POST method
            lecturerID = request.POST.get('lecturer')
            lecturer = Lecturer.objects.filter(id = lecturerID)[0]
            coords = request.POST.get('coords')

            now = datetime.datetime.now() # current date and time
            uniqueid = str(coords) + now.strftime("%H:%M:%S")
            newEvent = MapEvent(id = uniqueid, lec_id = lecturer, pos=coords, wildOrBattle=gameop)
            newEvent.save()

    items = [player.balls, player.extensions]
    # get all of the lecturers and map events
    lec = Lecturer.objects.all()
    mapEvent = MapEvent.objects.all()
    stops = LectStop.objects.all()
    return render(request, 'mapmod.html',{'lec': lec, 'mapEvent': mapEvent, 'stops': stops, 'items': items})


""" TRADE -------------------- """
def trade(request):

    if request.method == 'POST':
        print(request.POST)
        s = request.POST.get('sender')
        r = request.POST.get('reciever')
        #retrieve object
        sender = Player.objects.filter(username=s).first()
        reciever = Player.objects.get(username=r)
        print(sender ,"<--- sender")
        print(reciever ,"<--- reciever")
        #retrieve their lecturers
        sender_lects = Hand.objects.filter(username = sender.id)
        reciever_lects = Hand.objects.filter(username = reciever.id)
        # return the render with the lecturer and event IDs
        un = request.user.username
        # get the player object that matches the username
        player = Player.objects.filter(username=un)[0]
        items = [player.balls, player.extensions]

    return render(request, 'trade.html', {'sender':sender_lects,
                                        'sender_name':sender.username,
                                        'reciever_name': reciever.username,
                                         'reciever':reciever_lects,
                                         'is_admin': get_admin(request),
                                         'items' : items})

""" NEW TRADE ---------------- """
def newtrade(request):
    if request.method == 'POST':
        print(request.POST)
        l = request.POST.get('left')
        r = request.POST.get('right')

        current_user = request.user
        un = current_user.username
        player = Player.objects.filter(username=un)[0]

        lec = Lecturer.objects.filter()

        #addds the lec to the players hand
        player.pokemon_caught = player.pokemon_caught+1
        player.save()

        h = Hand(username = player, lec_id = l.lec_id)
        h.save()

    return render(request, 'lecturers.html', {})


""" get_admin ------------------- """
""" This method handles checks if the user is an admin. This then gives it to the template """
def get_admin(request):
    # get the user object from the request
    current_user = request.user
    # get the username of the user
    un = current_user.username
    # get player object by username from the database (filter returns a list)
    player = Player.objects.filter(username=un)[0]
    
    # return is_admin (boolean)
    return player.is_admin
