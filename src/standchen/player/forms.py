import math
from pathlib import Path
from typing import Any

from django.forms import (
    CheckboxSelectMultiple,
    IntegerField,
    ModelForm,
    CharField,
    ModelMultipleChoiceField,
    ValidationError,
)
import mutagen
from mutagen import FileType
from .models import Playlist, StandchenAudio

DUPLICATE_FILEPATH = "duplicate_filepath"


class NewAudioForm(ModelForm):
    class Meta:
        model = StandchenAudio
        fields = ["filepath", "title", "length"]

    filepath = CharField(error_messages={"unique": DUPLICATE_FILEPATH})
    title = CharField(required=False)
    length = IntegerField(required=False)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        fp = Path(cleaned_data.get("filepath"))
        if not fp.is_file():
            raise ValidationError("Filepath is not a file!", code="invalid")
        data = mutagen.File(fp)
        if not isinstance(data, FileType):
            raise ValidationError("File is invalid/corrupt.", code="invalid")

        cleaned_data["title"] = (
            cleaned_data.get("title") or data.get("title", [None])[0] or fp.name
        )
        cleaned_data["album"] = data.get("album", [None])[0]
        cleaned_data["artist"] = data.get("artist", [None])[0]
        cleaned_data["length"] = math.floor(data.info.length * 1000)
        return cleaned_data


class StandchenAudioChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj: StandchenAudio):
        return f"**{obj.title} ({obj.pretty_length()}): {obj.filepath}"


class NewPlaylistForm(ModelForm):
    class Meta:
        model = Playlist
        fields = ["title", "tracks"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    title = CharField(max_length=256)
    tracks = StandchenAudioChoiceField(
        queryset=StandchenAudio.objects.all(), widget=CheckboxSelectMultiple
    )
