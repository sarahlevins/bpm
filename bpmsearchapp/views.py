from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.urls import reverse

import requests
import pprint
import base64
import json
import os
from .forms import SearchForm, PlaylistForm
from .models import Track, Playlist

from .modules.spotify import SpotifyTrack


def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            track = Track.create_track(form.cleaned_data.get('song_title'))
            track.save()
            recommendations_playlist = Playlist.create_playlist(
                track, form.cleaned_data.get('target_tempo'), form.cleaned_data.get('duration'))
            return redirect('bpm:playlist', pk=recommendations_playlist.pk)
    else:
        form = SearchForm()
    return render(request, 'bpmsearchapp/index.html', {
        'form': form,
    })


def playlist(request, pk):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            request.session['playlist_name'] = form.cleaned_data.get('name')
            return redirect(f'https://accounts.spotify.com/authorize?client_id={os.environ.get("SPOTIFY_CLIENT_ID")}&response_type=code&redirect_uri={os.environ.get("REDIRECT_URI")}&scope=playlist-modify-private')
    else:
        form = PlaylistForm()
        request.session['playlist_pk'] = pk
        playlist = Playlist.objects.get(pk=pk)
    return render(request, 'bpmsearchapp/playlist.html', {
        'form': form,
        'playlist': playlist,
        'playlist_tracks': playlist.tracks.all(),
        'track': playlist.based_on})


def spotify_auth(request):
    request.session['auth_code'] = request.GET.get('code', '')
    playlist = get_object_or_404(
        Playlist, pk=request.session.get('playlist_pk'))
    playlist.name = request.session.get('playlist_name')
    playlist.save(update_fields=['name'])

    auth_response = requests.post(
        'https://accounts.spotify.com/api/token', data={
            'code': request.session['auth_code'],
            'client_id': os.environ.get('SPOTIFY_CLIENT_ID'),
            'client_secret': os.environ.get('SPOTIFY_CLIENT_SECRET'),
            'grant_type': 'authorization_code',
            'redirect_uri': os.environ.get("REDIRECT_URI")
        })

    user_id = requests.get('https://api.spotify.com/v1/me', headers={
        "Authorization": f"Bearer {auth_response.json()['access_token']}"}).json()['id']

    playlist_id = requests.post(f'https://api.spotify.com/v1/users/{user_id}/playlists',
                                headers={
                                    "Authorization": f"Bearer {auth_response.json()['access_token']}",
                                    "Content-Type": "application/json"
                                },
                                data=str(json.dumps(
                                    {"name": playlist.name, "public": "false"}))).json()['id']

    add_items_to_playlist_response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                                                   headers={
                                                       "Authorization": f"Bearer {auth_response.json()['access_token']}",
                                                       "Content-Type": "application/json"
                                                   },
                                                   data=playlist.recommended_id_string)

    return redirect('bpm:playlist',
                    pk=request.session['playlist_pk'])
