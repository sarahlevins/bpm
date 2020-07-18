from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

import requests, pprint, base64, json
from .forms import SearchForm
from .modules.spotify import pretty_time_delta, get_song_detail, get_audio_features, get_song_recommendations

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
            #get details of requested song
            song_detail = get_song_detail(song_title)
            song_detail['tempo'] = get_audio_features(song_detail['id'])['tempo']
            #get song recommendations
            song_recommendations = get_song_recommendations(song_detail['id'], target_tempo)
            song_recommendations.insert(0,song_detail)
            total_duration = 0
            for d in song_recommendations:
                total_duration += d['duration_ms']
            total_duration = pretty_time_delta(total_duration/1000)

            return render(request, 'bpmsearchapp/song.html', {'song_recommendations': song_recommendations, 'song_detail': song_detail, 'total_duration':total_duration})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()
    return render(request, 'bpmsearchapp/index.html', {'form': form})
