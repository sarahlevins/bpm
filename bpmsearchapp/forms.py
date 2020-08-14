from django import forms


class SearchForm(forms.Form):
    song_title = forms.CharField(label='Song title', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'eg. American Idiot'}))
    target_tempo = forms.CharField(
        label='Target tempo', max_length=3, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg. 170 (optional)'}))
    target_pace = forms.CharField(label='Target pace', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'eg. 5:45 (optional)'}))
    duration = forms.IntegerField(label='Duration in minutes', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'eg. 30 (optional)'}))


class PlaylistForm(forms.Form):
    name = forms.CharField(label='Save Playlist to Spotify', max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Playlist Name'}))
