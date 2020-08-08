from django.urls import path
from . import views

app_name = 'bpm'
urlpatterns = [
    path('', views.index, name='index')
]
