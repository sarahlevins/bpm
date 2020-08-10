from django import forms


class SearchForm(forms.Form):
    song_title = forms.CharField(label='Song title', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'eg. American Idiot'}))
    target_tempo = forms.CharField(
        label='Target tempo', max_length=3, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg. 170'}))
    duration = forms.IntegerField(label='Duration in minutes', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'eg. 30'}))


class PlaylistForm(forms.Form):
    name = forms.CharField(label='Save Playlist to Spotify', max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Playlist Name'}))
