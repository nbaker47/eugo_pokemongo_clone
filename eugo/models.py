""" ---------------------------- IMPORTS -------------------------------------------------------------- """
""" DJANGO IMPORTS ----------- """
from codecs import backslashreplace_errors
from django.db import models
from django.dispatch import receiver            # import models in order to create the models themselves
from django.utils import timezone       # import timezeone to be able to log events
from django.conf import settings
import uuid

""" OTHER IMPORTS ------------ """
import datetime               # import all from datetime to be able to log events


""" --------------------------- MODELS ---------------------------------------------------------------- """
""" PLAYER ------------------- """
""" Player table where we will store the personal account data for the user"""
class Player(models.Model):
    id               =   models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstname        =   models.CharField(max_length=30, null=True)
    surname          =   models.CharField(max_length=30, null=True)
    email            =   models.CharField(max_length=40, null=True)
    username         =   models.CharField(max_length=20)
    pokemon_caught   =   models.IntegerField(default=0)
    sprite_url       =   models.CharField(default="eugo\static\eugo\img\teacher_sprites\teacher_1.png", max_length=100, null=True)
    is_admin         =   models.BooleanField(default=False)
    balls           =   models.IntegerField(default=0)
    extensions      =   models.IntegerField(default=0)

    # return username when object printed
    def __str__(self):
        return(self.username)


""" LECTURER ----------------- """
""" Lecturer table where we will store lecturers (essentially like pokemon) with all their attributes,
    we will have every lecturer as their own object """
class Lecturer(models.Model):
    id              =   models.CharField(max_length=100, primary_key=True)
    name            =   models.CharField(max_length=100)
    hp              =   models.IntegerField()
    attack          =   models.IntegerField()
    sprite          =   models.CharField(max_length=100)
    type            =   models.CharField(max_length=100)
    duration        =   models.IntegerField()
    qrUrl           =   models.CharField(max_length=500)

    def __str__(self):
        return (self.name)


""" MAP EVENT ---------------- """
""" A model to track all of the events on the map """
class MapEvent(models.Model):
    id              =   models.CharField(max_length=100, primary_key=True)
    lec_id          =   models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    pos             =   models.CharField(max_length=100)
    wildOrBattle    =   models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class LectStop(models.Model):
    id              =   models.CharField(max_length=100, primary_key=True)
    balls           =   models.IntegerField()
    extensions      =   models.IntegerField()
    qrUrl           =   models.CharField(max_length=500)
    created_at      =   models.DateTimeField(auto_now_add=True)
    pos             =   models.CharField(max_length=100)


""" COMPLETE STOPS ---------- """
""" A table that will track all of the stops collected by a given player """
class CompleteStops(models.Model):
    username        =   models.ForeignKey(Player, on_delete=models.CASCADE)
    stop           =   models.ForeignKey(LectStop, on_delete=models.CASCADE)

""" COMPLETE EVENTS ---------- """
""" A table that will track all of the events completed by a given player """
class CompleteEvents(models.Model):
    username        =   models.ForeignKey(Player, on_delete=models.CASCADE)
    event           =   models.ForeignKey(MapEvent, on_delete=models.CASCADE)


""" HAND --------------------- """
""" A table to link the player with the lecturers they own """
class Hand(models.Model):
    username        =   models.ForeignKey(Player, on_delete=models.CASCADE)
    lec_id          =   models.ForeignKey(Lecturer, on_delete=models.CASCADE)

    # return the username and lecturer to show the link between 
    def __str__(self):
        return (str(self.username) + ": " + str(self.lec_id))


""" CHAT CHANNEL ------------- """
""" A table required for the chat box """
class ChatChannel(models.Model):
    channel_id      =   models.CharField(max_length=100, primary_key=True)
    channel_name    =   models.CharField(max_length=100)


"""" CHAT MESSAGES ----------- """
""" A table for all of the chat messages """
class ChatMessage(models.Model):
    channel_id      =   models.ForeignKey(ChatChannel, on_delete=models.CASCADE)
    user            =   models.CharField(max_length=20)
    content         =   models.CharField(max_length=100, default='message', null=True)
    date            =   models.TimeField(auto_now=False, default=timezone.now )

""" FRIENDS"""
""" keeps track of friends/blocked"""
class FriendsList(models.Model):
    user1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='user')
    friends = models.CharField(default='', max_length=2000)
    #relationship = models.IntegerField() #0=pending 1=friends 2=blocked
    #date_sent = models.DateField(auto_now=True=)

    def __str__(self) -> str:
        return self.user1.username

    def add_friend(self, user):
        print("ADDING A FIREIEAIWDNAD")
        self.friends = str(self.friends) + ',' + str(user.id)
        self.save()
    
    def remove_friend(self, user):
        if user in self.friends.all():
            self.friends.remove(user)
            self.save() 
    
    """
    def unfriend(self, removee):
        #remove both from eachothers friend list
        remover_friends_list = self
        remover_friends_list.remove_friend(removee)
        friends_list = FriendsList.objects.get(user=removee)
        friends_list.remove_friend(self.user)
    
    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        else:
            return False
    """            

"""Class for friend request"""
class FriendRequest(models.Model):
    sender = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="sender")
    reciever = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="reciever")
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.sender.username
    
    """When receiver accepts"""
    def accept(self):
        #update sender and reciever
        print("SELF RECIEVER: ", self.reciever)
        reciever_friend_list = FriendsList.objects.filter(user1=self.reciever)
        if reciever_friend_list:
            reciever_friend_list.add_friend(self.sender)
        else:
            reciever_friend_list = FriendsList.objects.create(user1=self.reciever)
            reciever_friend_list.add_friend(self.sender)
        
        sender_friend_list  = FriendsList.objects.filter(user1=self.sender)
        if sender_friend_list:
            sender_friend_list.add_friend(self.reciever)
        else:
            sender_friend_list = FriendsList.objects.create(user1=self.sender)
            sender_friend_list.add_friend(self.reciever)
        self.is_active = False
        self.save()
    
    """If reciever declines"""
    def decline(self):
        self.is_active = False
        self.save()

    """if sender cancels"""
    def cancel(self):
        self.is_active = False
        self.save()
