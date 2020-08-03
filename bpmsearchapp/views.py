from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

import requests
import pprint
import base64
import json
from .forms import SearchForm
from .modules.spotify import pretty_time_delta, Track


def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            song_title = form.cleaned_data.get('song_title')
            target_tempo = form.cleaned_data.get('target_tempo')
            duration = form.cleaned_data.get('duration')
            # get details of requested song
            track = Track(song_title)
            track.get_song_detail()
            track.get_song_recommendations(target_tempo)
            track.create_duration_playlist(duration)
            total_duration = 0
            for d in track.duration_playlist:
                total_duration += d.duration_ms
            total_duration = pretty_time_delta(total_duration/1000)

            return render(request, 'bpmsearchapp/song.html', {'song_recommendations': track.duration_playlist, 'track': track, 'total_duration': total_duration})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()
    return render(request, 'bpmsearchapp/index.html', {'form': form})
