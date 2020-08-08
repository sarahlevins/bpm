import os
import base64
import json
import requests
import datetime
import pprint
import numpy as np
from datetime import timedelta


def get_access_token():
    CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

    auth_str = bytes("{}:{}".format(CLIENT_ID, CLIENT_SECRET), "utf-8")
    b64_auth_str = base64.b64encode(auth_str).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    grant_type = {"grant_type": "client_credentials"}
    header = {"Authorization": "Basic {}".format(b64_auth_str)}

    return requests.post(url, data=grant_type, headers=header).json()["access_token"]


def pretty_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%s%dd%dh%dm%ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh%dm%ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%dm%ds' % (sign_string, minutes, seconds)
    else:
        return '%s%ds' % (sign_string, seconds)


class Track():
    def __init__(self, title):
        self.title = title

    def get_song_detail(self):
        access_token = get_access_token()
        header_list = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        track_detail_response = requests.get(
            f"https://api.spotify.com/v1/search?q={self.title}&type=track", headers=header_list).json()["tracks"]["items"][0]
        audio_features_response = requests.get(
            f"https://api.spotify.com/v1/audio-features?ids={track_detail_response['id']}", headers=header_list).json()['audio_features'][0]

        self.id = track_detail_response['id']
        self.duration_ms = track_detail_response['duration_ms']
        self.artist = track_detail_response['artists'][0]['name']
        self.duration = pretty_time_delta(
            int(track_detail_response['duration_ms']/1000))
        self.tempo = audio_features_response['tempo']
        return self

    def get_song_recommendations(self, tempo):
        access_token = get_access_token()
        header_list = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        self.recommendations = []
        recc_response = requests.get(
            f"https://api.spotify.com/v1/recommendations?market=AU&limit=90&seed_tracks={self.id}&target_tempo={tempo}", headers=header_list).json()['tracks']
        feat_response = requests.get(
            f"https://api.spotify.com/v1/audio-features/?ids={','.join([track['id'] for track in recc_response])}", headers=header_list).json()['audio_features']

        self.recommendation_ids = [track['id'] for track in recc_response]

        for i in enumerate(recc_response):
            i = i[0]
            track = Track(recc_response[i]['name'])
            track.artist = recc_response[i]['artists'][0]['name']
            track.duration_ms = recc_response[i]['duration_ms']
            track.id = recc_response[i]['id']
            track.tempo = feat_response[i]['tempo']
            track.duration = pretty_time_delta(
                int(recc_response[i]['duration_ms']/1000))
            self.recommendations.append(track)
        return self

    def create_duration_playlist(self, duration):
        if not self.recommendations:
            self.get_song_recommendations(self, 150)
        else:
            self.duration_playlist = [self]
            target_duration = datetime.timedelta(minutes=duration+3)
            duration = datetime.timedelta(minutes=0)
            for i in enumerate(self.recommendations):
                while duration < target_duration:
                    self.duration_playlist.append(self.recommendations[i[0]])
                    duration += datetime.timedelta(
                        milliseconds=self.recommendations[i[0]].duration_ms)
        self.duration_playlist_duration = np.sum(
            [t.duration_ms for t in self.duration_playlist])
        return self

    def spotify_playlist(self, playlist_name):
        spotify_user_auth_url = f'https://accounts.spotify.com/authorize?client_id={os.environ.get("SPOTIFY_CLIENT_ID")}&response_type=code&redirect_uri={os.environ.get("REDIRECT_URI")}&scope=playlist-modify-private'

        user_auth_response = requests.get(spotify_user_auth_url).json()

        print(user_auth_response)

        body = {
            'code': user_auth_response['code'],
            'client_id': os.environ.get('SPOTIFY_CLIENT_ID'),
            'client_secret': os.environ.get('SPOTIFY_CLIENT_SECRET'),
            'grant_type': 'authorization_code',
            'redirect_uri': os.environ.get("REDIRECT_URI")
        }
        auth_response = requests.post(
            'https://accounts.spotify.com/api/token', data=body)

        user_response = requests.get('https://api.spotify.com/v1/me', headers={
            "Authorization": f"Bearer {auth_response.json()['access_token']}"})

        user_id = user_response.json()['id']
        playlist_payload = '{\"name\":\"test playlist2\", \"public\":false}'

        create_playlist_response = requests.post(f'https://api.spotify.com/v1/users/{user_id}/playlists',
                                                 headers={
                                                     "Authorization": f"Bearer {auth_response.json()['access_token']}",
                                                     "Content-Type": "application/json"
                                                 },
                                                 data=playlist_payload)

        playlist_id = create_playlist_response.json()['id']

        songs_payload = [
            f"spotify:track:{track}" for track in self.recommendation_ids]
        songs_payload = json.dumps({"uris": songs_payload})

        # songs_payload = json.dumps({"uris": ["spotify:track:2qxXypNXOJZ5qUFdpzJ56n",
        #                                      "spotify:track:6QfnvcOKsdN4Q6exUWVuzn", "spotify:track:72vsd9IEBIonmvIY7TEjXK"]})

        add_items_to_playlist_response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                                                       headers={
                                                           "Authorization": f"Bearer {auth_response.json()['access_token']}",
                                                           "Content-Type": "application/json"
                                                       },
                                                       data=songs_payload)

        return self
