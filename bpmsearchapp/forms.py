from django import forms


class SearchForm(forms.Form):
    song_title = forms.CharField(label='song title', max_length=100)
    target_tempo = forms.CharField(label='target tempo', max_length=3)
    duration = forms.IntegerField(label='duration in minutes')


class PlaylistForm(forms.Form):
    name = forms.CharField(label='playlist name', max_length=50)
