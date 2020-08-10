from django.db import models
import os
import base64
import json
import requests
import datetime
import pprint
import numpy as np
from datetime import timedelta

from .modules.spotify import get_access_token, pretty_time_delta, track_detail_query, recommendations_query


class Track(models.Model):
    spotify_id = models.CharField(max_length=50)
    title = models.CharField(max_length=1000)
    artist = models.CharField(max_length=50)
    duration_ms = models.IntegerField()
    duration = models.CharField(max_length=50)
    tempo = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    def create_track(song_title):
        track = track_detail_query(song_title)
        return Track(
            spotify_id=track['spotify_id'],
            title=track['title'],
            artist=track['artist'],
            duration=track['duration'],
            duration_ms=track['duration_ms'],
            tempo=track['tempo']
        )


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    duration = models.DurationField()
    based_on = models.ForeignKey(
        Track, on_delete=models.CASCADE)
    tracks = models.ManyToManyField(Track, related_name='tracks')
    recommended_id_string = models.CharField(max_length=5000)

    def __str__(self):
        return self.name

    def create_playlist(track, tempo, duration):
        recommendations, recommendation_ids = recommendations_query(
            track.spotify_id, tempo)
        duration_playlist = [track]
        playlist_ids = [track.spotify_id]
        target_duration = datetime.timedelta(minutes=duration+3)
        duration = datetime.timedelta(minutes=0)
        for i in enumerate(recommendations):
            if duration < target_duration:
                recommended_track = Track(
                    spotify_id=i[1].spotify_id,
                    title=i[1].title,
                    artist=i[1].artist,
                    duration=i[1].duration,
                    duration_ms=i[1].duration_ms,
                    tempo=i[1].tempo
                )
                recommended_track.save()
                duration_playlist.append(recommended_track)
                playlist_ids.append(recommended_track.spotify_id)
                duration += datetime.timedelta(
                    milliseconds=recommendations[i[0]].duration_ms)
                print(duration)
            else:
                break
        playlist = Playlist(
            name='unnamed',
            duration=datetime.timedelta(milliseconds=np.sum(
                [t.duration_ms for t in duration_playlist]).item()),
            recommended_id_string=json.dumps({"uris": [
                f"spotify:track:{id}" for id in playlist_ids]}),
            based_on=track
        )
        playlist.save()
        for recommended_track in duration_playlist:
            playlist.tracks.add(recommended_track)
        playlist.save()
        return playlist
