""" ---------------------------- IMPORTS -------------------------------------------------------------- """
""" DJANGO IMPORTS ----------- """
from django.db import models            # import models in order to create the models themselves
from django.utils import timezone       # import timezeone to be able to log events

""" OTHER IMPORTS ------------ """
# import datetime                           # import all from datetime to be able to log events


""" --------------------------- MODELS ---------------------------------------------------------------- """
""" PLAYER ------------------- """
""" Player table where we will store the personal account data for the user"""
class Player(models.Model):
    firstname        =   models.CharField(max_length=30, null=True)
    surname          =   models.CharField(max_length=30, null=True)
    email            =   models.CharField(max_length=40, null=True)
    username         =   models.CharField(max_length=20)
    pokemon_caught   =   models.IntegerField(default=0)
    sprite_url       =   models.CharField(default="eugo\static\eugo\img\teacher_sprites\teacher_1.png", max_length=100, null=True)
    is_admin         =   models.BooleanField(default=False)

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
        return (self.username + ": " + self.lec_id)


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