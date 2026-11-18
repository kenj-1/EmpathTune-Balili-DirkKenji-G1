from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from .models import MoodTag, Track


class TrackForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        required=True,
        strip=False,
        error_messages={"required": "Track title is required."},
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g., Clair de Lune",
            }
        ),
    )
    artist = forms.CharField(
        max_length=200,
        required=True,
        strip=False,
        error_messages={"required": "Artist name is required."},
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g., Claude Debussy",
            }
        ),
    )
    moods = forms.ModelMultipleChoiceField(
        queryset=MoodTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        help_text="Select one or more mood tags that match this track.",
    )

    class Meta:
        model = Track
        fields = ("title", "artist", "album", "genre", "preview_url", "moods")
        widgets = {
            "album": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Suite bergamasque (Optional)",
                }
            ),
            "genre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Ambient / Classical / Lo-Fi",
                }
            ),
            "preview_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://open.spotify.com/track/... (Optional)",
                }
            ),
        }
        error_messages = {
            "preview_url": {
                "invalid": "Please enter a valid URL starting with http:// or https://.",
            },
        }

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise ValidationError("Track title cannot be blank or whitespace only.")
        return title

    def clean_artist(self):
        artist = (self.cleaned_data.get("artist") or "").strip()
        if not artist:
            raise ValidationError("Artist name cannot be blank or whitespace only.")
        return artist

    def clean_album(self):
        return (self.cleaned_data.get("album") or "").strip()

    def clean_genre(self):
        return (self.cleaned_data.get("genre") or "").strip()

    def clean_preview_url(self):
        url = (self.cleaned_data.get("preview_url") or "").strip()
        if url:
            validator = URLValidator(schemes=["http", "https"])
            try:
                validator(url)
            except ValidationError:
                raise ValidationError(
                    "Please enter a valid preview URL starting with http:// or https://."
                )
        return url
