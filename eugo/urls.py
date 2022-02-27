from django.urls import path

from . import views

""" All of the urls and extensions that we have made, all of them are /eugo/{} """
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('map/', views.map, name='map'),
    path('battle/', views.battle, name='battle'),
    path('player/', views.player, name='player'),
    path('lecturers/', views.lecturers, name='lecturers'),
    path('lecturerdex/', views.lecturerdex, name='lecturerdex'),
    path('mapmod/', views.mapmod, name='mapmod'),
    path('catch/', views.catch, name='catch'),
    path('newcatch/', views.catch, name='newcatch'),
]
