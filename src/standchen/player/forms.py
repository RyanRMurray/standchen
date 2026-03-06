import math
from pathlib import Path
from typing import Any

from django.forms import IntegerField, ModelForm, CharField, ValidationError
import mutagen
from mutagen import FileType
from .models import StandchenAudio


class NewAudioForm(ModelForm):
    class Meta:
        model = StandchenAudio
        fields = ["filepath", "title", "length"]

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
        print(cleaned_data)
        return cleaned_data
