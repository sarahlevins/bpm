from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.urls import reverse


import requests
import pprint
import base64
import json
import os
from .forms import SearchForm, PlaylistForm
from .modules.spotify import pretty_time_delta, Track


def index(request):
    spotify_auth_url = f'https://accounts.spotify.com/authorize?client_id={os.environ.get("SPOTIFY_CLIENT_ID")}&response_type=code&redirect_uri={os.environ.get("REDIRECT_URI")}&scope=playlist-modify-private'
    if request.method == 'POST':
        form = SearchForm(request.POST)
        playlist_form = PlaylistForm(request.POST)
        if form.is_valid():
            track = Track(form.cleaned_data.get('song_title'))
            track.get_song_detail()
            track.get_song_recommendations(
                form.cleaned_data.get('target_tempo'))
            track.create_duration_playlist(form.cleaned_data.get('duration'))
            return render(request, 'bpmsearchapp/song.html', {'playlist_form': playlist_form, 'track': track, 'spotify_auth_url': spotify_auth_url, 'total_duration': pretty_time_delta(track.duration_playlist_duration/1000)})
        if playlist_form.is_valid():
            track = track
            playlist_name = playlist_form.cleaned_data.get(
                'playlist_name')
            track.spotify_playlist(playlist_name)
            return render(request, 'bpmsearchapp/song.html', {'success': 'success'})
    else:
        form = SearchForm()
    return render(request, 'bpmsearchapp/index.html', {'form': form})


def track(request, track):


def created_playlist(request):
    body = {
        'code': request.GET.get('code', ''),
        'client_id': os.environ.get('SPOTIFY_CLIENT_ID'),
        'client_secret': os.environ.get('SPOTIFY_CLIENT_SECRET'),
        'grant_type': 'authorization_code',
        'redirect_uri': os.environ.get("REDIRECT_URI")
    }
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token', data=body)

    print(auth_response)

    user_response = requests.get('https://api.spotify.com/v1/me', headers={
        "Authorization": f"Bearer {auth_response.json()['access_token']}"})

    user_id = user_response.json()['id']
    playlist_payload = "{\"name\":\"test playlist\", \"public\":false}"

    create_playlist_response = requests.post(f'https://api.spotify.com/v1/users/{user_id}/playlists',
                                             headers={
                                                 "Authorization": f"Bearer {auth_response.json()['access_token']}",
                                                 "Content-Type": "application/json"
                                             },
                                             data=playlist_payload)

    playlist_id = create_playlist_response.json()['id']

    songs_payload = json.dumps({"uris": ["spotify:track:2qxXypNXOJZ5qUFdpzJ56n",
                                         "spotify:track:6QfnvcOKsdN4Q6exUWVuzn", "spotify:track:72vsd9IEBIonmvIY7TEjXK"]})

    add_items_to_playlist_response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                                                   headers={
                                                       "Authorization": f"Bearer {auth_response.json()['access_token']}",
                                                       "Content-Type": "application/json"
                                                   },
                                                   data=songs_payload)

    return HttpResponseRedirect('bpmsearchapp/playlist.html', {'response': add_items_to_playlist_response})
