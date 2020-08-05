from django.urls import path
from . import views

app_name = 'bpm'
urlpatterns = [
    path('', views.index, name='index'),
    path('created_playlist/', views.created_playlist, name='created_playlist')]
