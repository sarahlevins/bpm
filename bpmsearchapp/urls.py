from django.urls import path
from . import views

app_name = 'bpm'
urlpatterns = [
    path('', views.index, name='index'),
    path('playlist/<int:pk>', views.playlist, name='playlist'),
    path('spotifyauth/',
         views.spotify_auth, name='spotify-auth')]
