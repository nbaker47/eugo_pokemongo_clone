from django.db import models

# here are all of the database tables, class name corresponds to table name

""" Player table where we will store the personal account data for the user"""
class Player(models.Model):
   firstname        =   models.CharField(max_length=30, null=True)
   surname          =   models.CharField(max_length=30, null=True)
   email            =   models.CharField(max_length=40, null=True)
   username         =   models.CharField(max_length=20)
   pokemon_caught   =   models.IntegerField(default=0)
   sprite_url       =   models.CharField(default="eugo\static\eugo\img\teacher_sprites\teacher_1.png", max_length=100, null=True)
   is_admin         =   models.BooleanField(default=False)

   def __str__(self):
       return(self.username)

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

"""a battle or cpture event on the map"""
class MapEvent(models.Model):
    lec_id          =   models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    pos             =   models.CharField(max_length=100)
    wildOrBattle    =   models.CharField(max_length=100)

""" A table to link the player with the lecturers they own """
class Hand(models.Model):
    username        =   models.ForeignKey(Player, on_delete=models.CASCADE)
    lec_id          =   models.ForeignKey(Lecturer, on_delete=models.CASCADE)

    def __str__(self):
        return (self.username + ": " + self.lec_id)
