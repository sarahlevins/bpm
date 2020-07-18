import os
import base64, json, requests, datetime

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


def get_song_detail(song_title):
    access_token = get_access_token()
    url = f"https://api.spotify.com/v1/search?q={song_title}&type=track"
    header_list = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=header_list).json()["tracks"]["items"][0]
    print(response)
    song_detail = {
        'song_title': response['name'],
        'id': response['id'],
        'duration_ms': response['duration_ms'],
        'artist': response['artists'][0]['name'],
        'duration': pretty_time_delta(int(response['duration_ms']/1000))
    }
    return song_detail

def get_audio_features(song_id):
    access_token = get_access_token()
    url = f"https://api.spotify.com/v1/audio-features?ids={song_id}"
    header_list = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    return requests.get(url, headers=header_list).json()['audio_features'][0]

def get_song_recommendations(song_id, tempo):
    access_token = get_access_token()
    url = f"https://api.spotify.com/v1/recommendations?market=AU&limit=10&seed_tracks={song_id}&target_tempo={tempo}"
    header_list = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    recommendations = []
    response = requests.get(url, headers=header_list).json()['tracks']

    for i in range(10):
        audio_features=get_audio_features(response[i]['id'])
        recommendations.append(
            {
            'artist' : response[i]['artists'][0]['name'],
            'song_title' : response[i]['name'],
            'duration_ms' : response[i]['duration_ms'],
            'tempo' : audio_features['tempo'],
            'id' : response[i]['id'],
            'duration': pretty_time_delta(int(response[i]['duration_ms']/1000))
            }
        )
    return recommendations