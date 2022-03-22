from django.urls import path

from . import views

""" All of the urls and extensions that we have made, all of them are /eugo/{} """
urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', views.signin, name='login'),
    path('logout/', views.signout, name='logout'),
    path('register/', views.register, name='register'),
    path('map/', views.map, name='map'),
    path('battle/', views.battle, name='battle'),
    path('player/', views.player, name='player'),
    path('lecturers/', views.lecturers, name='lecturers'),
    path('lecturerdex/', views.lecturerdex, name='lecturerdex'),
    path('mapmod/', views.mapmod, name='mapmod'),
    path('catch/', views.catch, name='catch'),
    path('newcatch/', views.newcatch, name='newcatch'),
    path('nocatch/', views.nocatch, name='nocatch'),
    path('friendreq/', views.friendreq, name='friendreq'),
    #path('sendchat/', views.sendchat, name = 'sendchat' ),
    path('trade/', views.trade, name='trade'),
    path('newtrade/', views.newtrade, name='newtrade'),
]
#login is 'signin' and log out is 'signout' in views because of a function imported with the same name