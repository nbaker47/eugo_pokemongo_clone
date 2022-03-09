""" ---------------------------- IMPORTS -------------------------------------------------------------- """
""" IMPORTS FROM EUGO -------- """
from eugo.models import *                                       # import the models (database)
from eugo.forms import *                                        # all of the forms ????????? TODO

""" IMPORTS FROM DJANGO ------ """
from django.shortcuts import redirect, render                   # to render templates and redirect 
from django.http import HttpResponse                            # send a http response using django
from django.template import loader# """ TODO: DEAD IMPORT? """
from django.shortcuts import get_object_or_404 #""" TODO: DEAD IMPORT? """
from django.contrib.auth.models import User                     # to be able to access the user database
from django.contrib.auth import authenticate, login, logout     # built in django methods that handle the
                                                                # user moving through pages
from django.contrib import messages                             # handle sending messages to the client 
from django.db import IntegrityError                            # throw integrity errors (database)

""" OTHER IMPORTS ------------ """
import requests                                                 # for the image data
import qrtools                                                  # for scanning and recognising the qr code
import re                                                       # for regex patterns
from random import randint                                      # random is self-explanatory
import datetime

""" ---------------------------- VIEWS ---------------------------------------------------------------- """
""" INDEX -------------------- """
""" This method to handle index.html (not much going on because this is just teh cover page) """
def index(request):
    return render(request, 'index.html')


""" BATTLE ------------------- """
""" This method to handle the battle.html """
def battle(request):
    return render(request, 'battle.html')


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
        sprite_no   =   request.POST['sprite']
        sprite_url  =   "eugo/static/eugo/img/teacher_sprites/teacher_" + sprite_no + ".png"
        print("SPRITE URL::   " + sprite_url)

        # try to make the new user in the database
        try:
            # create the new user object in the database and assign attributes
            user = User.objects.create_user(username, email, password)
            user.first_name = firstname
            user.last_name = surname
            # save the user in the User database
            user.save()

            # create a new player in the Player database
            p = Player(firstname = firstname, surname = surname, email = email, username = username, pokemon_caught = 0, sprite_url = sprite_url)
            # save the player in the Player database
            p.save()

            # print for debugging
            print(p)
            print(user)

            #make friends list
            fl = FriendsList(user1 = p)
            fl.save()

            # redirect to login screen (register successful)
            return redirect('/eugo/login/')

        # catch integrity errors (problem with database -> not registered)
        except IntegrityError as e:
            # semd appropriate messages to notify the user of the errors
            #messages.error(sprite_url)
            #messages.error(request, e)
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
            return render(request, "player.html", {"player":player_img})

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

    # finally, return the rendered template with the hand
    return render(request, 'lecturers.html',{'hand': hands})


""" LECTURERDEX -------------- """
""" This method handles the lecturerdex link """
def lecturerdex(request):
    # get a list of all of the lecturers
    lec = Lecturer.objects.all()
    # return the render with the lecturers list
    return render(request, 'lecturerdex.html',{'lec': lec})


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
    return render(request, 'catch.html',{'lec': lec, 'eve': event_id})


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


"""
def sendchat(request):
    if request.method == 'POST':
        try:
            channel_id = str(request.POST.get('channel'))
            username = str(request.POST.get('user'))
            message = str(request.POST.get('message'))
            channel_id_k = ChatChannel.objects.filter(channel_id  = channel_id)[0]
            new_message = ChatMessage(channel_id = channel_id_k , user = username, content=message)
            new_message.save()
            print("message : " + message)
        except Exception as e:
            print(e)
            
    return render(request, 'map.html')
"""


""" MAP ---------------------- """
""" This method handles the map link and its forms """
def map(request):
    # check if the request method is POST (corresponding to QR scans)
    if request.method == 'POST':
        # if it is get the QR URL
        qrUrl = request.POST['qrUrl']
        # try decoding the QR
        try:
            qr = qrtools.QR()
            qr.decode(qrUrl)
            print (qr.data)
        except:
            print('error reading QR')

    # load the lecturer object on the map
    lec = Lecturer.objects.all()
    # load the player objects on the map
    players = Player.objects.all()
    player_vals = players.values()
    # fetch and sort the leaderboard
    leaderboard = sorted(player_vals, key=lambda d: d['pokemon_caught'], reverse=True)
   
    # get all of the chat messages
    all_messages = ChatMessage.objects.all()
    #print(leaderboard)
    # get a list of all of the events on the map
    mapEvent = list(MapEvent.objects.all())
    
    #remove completed events
    completed_events = CompleteEvents.objects.all()
    for i in completed_events:
        mapEvent.remove(i.event)
    
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
        friends = []
        friends.append(FriendsList.objects.get(user1= user))
    except:
        pass
    
    print("FRIENDS :", friends)
    # return the html render, giving it all of the corresponding data
    return render(request, 'map.html',{'lec': lec, 'players': leaderboard, 'mapEvent': mapEvent, 'incomingReq': incoming_friend_req, 'friends': friends})


"""FRIEND REQ"""
def friendreq(request):
    if request.method == 'POST':
        #retrieve sender/recipient post data:
        type = request.POST['type']
        sender_name = request.POST['sender']
        sender = Player.objects.get(username = sender_name)
        reciever_name = request.POST['reciever']
        reciever = Player.objects.get(username = reciever_name)
        #send or accept request?
        if type == 'send':
            new_friend_req = FriendRequest(sender=sender, reciever=reciever)
            new_friend_req.save()
            print(new_friend_req)
            messages.success(request, "friend request sent" )
        elif type == 'accept':
            friend_req = FriendRequest.objects.get(sender=sender, reciever=reciever)
            friend_req.accept()
    return render(request, 'map.html')

""" MAPMOD ------------------- """
""" This method handles the mapmod link (admin map) and the ability to add more events """
def mapmod(request):
    # check if the request method is POST (a new event is being added)
    if request.method == 'POST':
        # get the operation being performed from the admin
        gameop = request.POST.get('gameop')
        print(gameop + "wut")
        print("test")
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
            qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + qr_key
            # save the QR to the file
            img_data = requests.get(qrUrl).content
            file_path = 'eugo/static/eugo/img/qr/' + qr_key + '.png' 
            with open(file_path, 'wb') as handler:
                handler.write(img_data)
            # create the new lecturer int eh Lecturer table
            newLec = Lecturer(id=qr_key, duration=duration, name=name, hp=hp, attack=attack, sprite=sprite, type=type, qrUrl = qr_key+'.png')
            # save the new lecturer
            newLec.save()
            print(newLec)
        
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

    # get all of the lecturers and map events
    lec = Lecturer.objects.all()
    mapEvent = MapEvent.objects.all()
    # return the render while giving it the lecturers and mapEvents arrays
    return render(request, 'mapmod.html',{'lec': lec, 'mapEvent': mapEvent})
